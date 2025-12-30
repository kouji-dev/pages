#!/usr/bin/env python3
"""Script unifié pour auditer et synchroniser les migrations de base de données.

Ce script permet de :
- Comparer la structure de la base de données avec les modèles SQLAlchemy
- Détecter les colonnes, index et contraintes manquants
- Générer un script SQL pour appliquer les corrections
- Vérifier l'état des migrations Alembic
"""

import argparse
import asyncio
import sys
from collections import defaultdict
from pathlib import Path

# Add the project root to the path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy import inspect  # noqa: E402

from src.infrastructure.database.config import Base, get_engine  # noqa: E402
from src.infrastructure.database.models import *  # noqa: F403, F401, E402


async def get_db_structure():
    """Get all tables, columns, indexes from the database."""
    engine = get_engine()

    db_structure = {}

    async with engine.begin() as conn:

        def get_tables(sync_conn):
            inspector = inspect(sync_conn)
            return inspector.get_table_names()

        tables = await conn.run_sync(get_tables)

        for table_name in tables:
            if table_name == "alembic_version":
                continue

            # Create a closure that captures table_name as a parameter
            def get_table_info_factory(tbl_name: str):
                def get_table_info(sync_conn):
                    inspector = inspect(sync_conn)
                    return {
                        "columns": inspector.get_columns(tbl_name),
                        "indexes": inspector.get_indexes(tbl_name),
                        "foreign_keys": inspector.get_foreign_keys(tbl_name),
                    }

                return get_table_info

            table_info = await conn.run_sync(get_table_info_factory(table_name))

            db_structure[table_name] = {
                "columns": {col["name"]: col for col in table_info["columns"]},
                "indexes": {idx["name"]: idx for idx in table_info["indexes"]},
                "foreign_keys": table_info["foreign_keys"],
            }

    await engine.dispose()
    return db_structure


def get_model_structure():
    """Get all tables, columns, indexes from SQLAlchemy models."""
    model_structure = {}

    for table_name, table in Base.metadata.tables.items():
        if table_name == "alembic_version":
            continue

        columns = {}
        for column in table.columns:
            columns[column.name] = {
                "type": str(column.type),
                "nullable": column.nullable,
                "default": str(column.default) if column.default else None,
            }

        indexes = {}
        for index in table.indexes:
            indexes[index.name] = {
                "columns": [col.name for col in index.columns],
                "unique": index.unique,
            }

        foreign_keys = []
        for fk in table.foreign_keys:
            foreign_keys.append(
                {
                    "column": fk.parent.name,
                    "referred_table": fk.column.table.name,
                    "referred_column": fk.column.name,
                }
            )

        model_structure[table_name] = {
            "columns": columns,
            "indexes": indexes,
            "foreign_keys": foreign_keys,
        }

    return model_structure


def compare_structures(db_structure, model_structure):
    """Compare database structure with model structure."""
    issues = {
        "missing_tables": [],
        "extra_tables": [],
        "missing_columns": defaultdict(list),
        "extra_columns": defaultdict(list),
        "missing_indexes": defaultdict(list),
        "extra_indexes": defaultdict(list),
    }

    # Check tables
    db_tables = set(db_structure.keys())
    model_tables = set(model_structure.keys())

    issues["missing_tables"] = sorted(model_tables - db_tables)
    issues["extra_tables"] = sorted(db_tables - model_tables)

    # Check columns for common tables
    common_tables = db_tables & model_tables
    for table_name in common_tables:
        db_cols = set(db_structure[table_name]["columns"].keys())
        model_cols = set(model_structure[table_name]["columns"].keys())

        missing = model_cols - db_cols
        extra = db_cols - model_cols

        if missing:
            issues["missing_columns"][table_name] = sorted(missing)
        if extra:
            issues["extra_columns"][table_name] = sorted(extra)

    # Check indexes for common tables
    for table_name in common_tables:
        db_indexes = set(db_structure[table_name]["indexes"].keys())
        model_indexes = set(model_structure[table_name]["indexes"].keys())

        missing = model_indexes - db_indexes
        extra = db_indexes - model_indexes

        if missing:
            issues["missing_indexes"][table_name] = sorted(missing)
        if extra:
            issues["extra_indexes"][table_name] = sorted(extra)

    return issues


def generate_sql_fix(issues, model_structure):
    """Generate SQL script to fix missing columns and indexes."""
    sql_lines = [
        "-- Script généré automatiquement pour corriger les différences",
        "-- entre la base de données et les modèles SQLAlchemy",
        "",
    ]

    # Add missing columns
    for table_name, columns in sorted(issues["missing_columns"].items()):
        for col_name in columns:
            col_info = model_structure[table_name]["columns"][col_name]
            col_type = col_info["type"]

            # Map SQLAlchemy types to PostgreSQL types
            type_mapping = {
                "VARCHAR": "VARCHAR",
                "String": "VARCHAR(255)",
                "Text": "TEXT",
                "Integer": "INTEGER",
                "Boolean": "BOOLEAN",
                "DateTime": "TIMESTAMP WITH TIME ZONE",
                "Date": "DATE",
                "UUID": "UUID",
            }

            pg_type = col_type
            for key, value in type_mapping.items():
                if key in col_type:
                    pg_type = value
                    break

            nullable = "NULL" if col_info["nullable"] else "NOT NULL"
            default = ""
            if col_info["default"]:
                if "now()" in col_info["default"].lower():
                    default = " DEFAULT NOW()"
                elif col_info["default"]:
                    default = f" DEFAULT {col_info['default']}"

            sql_lines.append(f"-- Colonne {col_name} dans {table_name}")
            sql_lines.append(
                f"ALTER TABLE {table_name} "
                f"ADD COLUMN IF NOT EXISTS {col_name} {pg_type} {nullable}{default};"
            )

    # Add missing indexes
    for table_name, indexes in sorted(issues["missing_indexes"].items()):
        for idx_name in indexes:
            idx_info = model_structure[table_name]["indexes"][idx_name]
            cols = ", ".join(idx_info["columns"])
            unique = "UNIQUE " if idx_info["unique"] else ""

            sql_lines.append(f"-- Index {idx_name} sur {table_name}")
            sql_lines.append(
                f"CREATE {unique}INDEX IF NOT EXISTS {idx_name} " f"ON {table_name}({cols});"
            )

    return "\n".join(sql_lines)


async def audit_database(verbose=False, generate_sql=False):
    """Main audit function."""
    print("=" * 80)
    print("AUDIT DES MIGRATIONS DE BASE DE DONNÉES")
    print("=" * 80)
    print()

    print("📊 Récupération de la structure de la base de données...")
    try:
        db_structure = await get_db_structure()
        print(f"   ✅ {len(db_structure)} tables trouvées dans la base de données")
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
        return 1

    print("📊 Récupération de la structure des modèles...")
    model_structure = get_model_structure()
    print(f"   ✅ {len(model_structure)} tables trouvées dans les modèles")
    print()

    print("🔍 Comparaison des structures...")
    issues = compare_structures(db_structure, model_structure)
    print()

    # Report results
    print("=" * 80)
    print("RÉSULTATS DE LA COMPARAISON")
    print("=" * 80)
    print()

    total_issues = 0

    if issues["missing_tables"]:
        print(f"⚠️  TABLES MANQUANTES DANS LA BASE DE DONNÉES ({len(issues['missing_tables'])}):")
        for table in issues["missing_tables"]:
            print(f"   - {table}")
        print()
        total_issues += len(issues["missing_tables"])

    if issues["extra_tables"]:
        print(f"ℹ️  TABLES SUPPLÉMENTAIRES DANS LA BASE DE DONNÉES ({len(issues['extra_tables'])}):")
        for table in issues["extra_tables"]:
            print(f"   - {table}")
        print()

    if issues["missing_columns"]:
        print("⚠️  COLONNES MANQUANTES DANS LA BASE DE DONNÉES:")
        for table, cols in sorted(issues["missing_columns"].items()):
            print(f"   Table '{table}':")
            for col in cols:
                print(f"      - {col}")
        print()
        total_issues += len(issues["missing_columns"])

    if issues["extra_columns"]:
        if verbose:
            print("ℹ️  COLONNES SUPPLÉMENTAIRES DANS LA BASE DE DONNÉES:")
            for table, cols in sorted(issues["extra_columns"].items()):
                print(f"   Table '{table}':")
                for col in cols:
                    print(f"      - {col}")
            print()

    if issues["missing_indexes"]:
        print("⚠️  INDEX MANQUANTS DANS LA BASE DE DONNÉES:")
        for table, idxs in sorted(issues["missing_indexes"].items()):
            print(f"   Table '{table}':")
            for idx in idxs:
                print(f"      - {idx}")
        print()
        total_issues += len(issues["missing_indexes"])

    if issues["extra_indexes"]:
        if verbose:
            print("ℹ️  INDEX SUPPLÉMENTAIRES DANS LA BASE DE DONNÉES:")
            for table, idxs in sorted(issues["extra_indexes"].items()):
                print(f"   Table '{table}':")
                for idx in idxs:
                    print(f"      - {idx}")
            print()

    # Summary
    if total_issues == 0:
        print(
            "✅ Aucune différence détectée ! La base de données est synchronisée avec les modèles."
        )
        return 0
    else:
        print(f"⚠️  {total_issues} problème(s) détecté(s) nécessitant des migrations.")
        print()

        if generate_sql:
            sql_script = generate_sql_fix(issues, model_structure)
            output_file = project_root / "scripts" / "fix_migrations.sql"
            output_file.write_text(sql_script)
            print(f"📝 Script SQL généré : {output_file}")
            print("   Vous pouvez l'appliquer avec :")
            print(f"   psql -U postgres -d pages -f {output_file}")
            print()

        return 1


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Audit des migrations de base de données",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples:
  # Audit simple
  python scripts/migration_audit.py

  # Audit avec détails supplémentaires
  python scripts/migration_audit.py --verbose

  # Audit et génération du script SQL de correction
  python scripts/migration_audit.py --generate-sql
        """,
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Afficher les détails supplémentaires (colonnes/index supplémentaires)",
    )
    parser.add_argument(
        "-g",
        "--generate-sql",
        action="store_true",
        help="Générer un script SQL pour corriger les différences",
    )

    args = parser.parse_args()

    exit_code = asyncio.run(
        audit_database(
            verbose=args.verbose,
            generate_sql=args.generate_sql,
        )
    )

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
