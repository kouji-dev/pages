-- Script pour appliquer les colonnes et index manquants
-- Basé sur l'audit des différences entre les migrations et la base de données

-- ============================================================================
-- 1. Users.language (Migration: 46fc6f4041c4)
-- ============================================================================
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'users' AND column_name = 'language'
    ) THEN
        ALTER TABLE users ADD COLUMN language VARCHAR(5) NOT NULL DEFAULT 'en';
        CREATE INDEX ix_users_language ON users(language);
        RAISE NOTICE 'Colonne language ajoutée à users';
    ELSE
        RAISE NOTICE 'Colonne language existe déjà dans users';
    END IF;
END $$;

-- ============================================================================
-- 2. Issues.backlog_order (Migration: add_sprints_backlog)
-- ============================================================================
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'issues' AND column_name = 'backlog_order'
    ) THEN
        ALTER TABLE issues ADD COLUMN backlog_order INTEGER;
        CREATE INDEX ix_issues_backlog_order ON issues(backlog_order);
        RAISE NOTICE 'Colonne backlog_order ajoutée à issues';
    ELSE
        RAISE NOTICE 'Colonne backlog_order existe déjà dans issues';
    END IF;
END $$;

-- ============================================================================
-- 3. Issues.parent_issue_id (Migration: 3c8bea2ce013)
-- ============================================================================
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'issues' AND column_name = 'parent_issue_id'
    ) THEN
        ALTER TABLE issues ADD COLUMN parent_issue_id UUID;
        ALTER TABLE issues ADD CONSTRAINT fk_issues_parent_issue_id 
            FOREIGN KEY (parent_issue_id) REFERENCES issues(id) ON DELETE SET NULL;
        CREATE INDEX ix_issues_parent_issue_id ON issues(parent_issue_id);
        RAISE NOTICE 'Colonne parent_issue_id ajoutée à issues';
    ELSE
        RAISE NOTICE 'Colonne parent_issue_id existe déjà dans issues';
    END IF;
END $$;

-- ============================================================================
-- 4. Projects.folder_id (Migration: 1432f294aabb)
-- ============================================================================
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'projects' AND column_name = 'folder_id'
    ) THEN
        -- Vérifier que la table folders existe
        IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'folders') THEN
            ALTER TABLE projects ADD COLUMN folder_id UUID;
            ALTER TABLE projects ADD CONSTRAINT fk_projects_folder_id 
                FOREIGN KEY (folder_id) REFERENCES folders(id) ON DELETE SET NULL;
            CREATE INDEX ix_projects_folder_id ON projects(folder_id);
            RAISE NOTICE 'Colonne folder_id ajoutée à projects';
        ELSE
            RAISE WARNING 'Table folders n''existe pas, folder_id non ajouté à projects';
        END IF;
    ELSE
        RAISE NOTICE 'Colonne folder_id existe déjà dans projects';
    END IF;
END $$;

-- ============================================================================
-- 5. Spaces.folder_id (Migration: 1432f294aabb)
-- ============================================================================
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'spaces' AND column_name = 'folder_id'
    ) THEN
        -- Vérifier que la table folders existe
        IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'folders') THEN
            ALTER TABLE spaces ADD COLUMN folder_id UUID;
            ALTER TABLE spaces ADD CONSTRAINT fk_spaces_folder_id 
                FOREIGN KEY (folder_id) REFERENCES folders(id) ON DELETE SET NULL;
            CREATE INDEX ix_spaces_folder_id ON spaces(folder_id);
            RAISE NOTICE 'Colonne folder_id ajoutée à spaces';
        ELSE
            RAISE WARNING 'Table folders n''existe pas, folder_id non ajouté à spaces';
        END IF;
    ELSE
        RAISE NOTICE 'Colonne folder_id existe déjà dans spaces';
    END IF;
END $$;

-- ============================================================================
-- 6. Templates.category (Migration: 9b0c1d2e3f4a)
-- ============================================================================
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'templates' AND column_name = 'category'
    ) THEN
        ALTER TABLE templates ADD COLUMN category VARCHAR(50);
        RAISE NOTICE 'Colonne category ajoutée à templates';
    ELSE
        RAISE NOTICE 'Colonne category existe déjà dans templates';
    END IF;
END $$;

-- ============================================================================
-- Vérification finale
-- ============================================================================
SELECT 
    'Résumé des colonnes ajoutées' as info,
    (SELECT COUNT(*) FROM information_schema.columns WHERE table_name = 'users' AND column_name = 'language') as users_language,
    (SELECT COUNT(*) FROM information_schema.columns WHERE table_name = 'issues' AND column_name = 'backlog_order') as issues_backlog_order,
    (SELECT COUNT(*) FROM information_schema.columns WHERE table_name = 'issues' AND column_name = 'parent_issue_id') as issues_parent_issue_id,
    (SELECT COUNT(*) FROM information_schema.columns WHERE table_name = 'projects' AND column_name = 'folder_id') as projects_folder_id,
    (SELECT COUNT(*) FROM information_schema.columns WHERE table_name = 'spaces' AND column_name = 'folder_id') as spaces_folder_id,
    (SELECT COUNT(*) FROM information_schema.columns WHERE table_name = 'templates' AND column_name = 'category') as templates_category;

