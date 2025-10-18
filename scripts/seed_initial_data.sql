-- Initial Data Population for Issue Tracker
-- This script populates essential data needed for the application to function

-- ============================================
-- 1. STATUSES (Required for issues)
-- ============================================
INSERT INTO statuses (id, name, display_order) VALUES
(1, 'Open', 1),
(2, 'In Progress', 2),
(3, 'Resolved', 3),
(4, 'Closed', 4),
(5, 'Reopened', 5)
ON CONFLICT (id) DO NOTHING;

-- Reset sequence for statuses
SELECT setval('statuses_id_seq', (SELECT MAX(id) FROM statuses));

-- ============================================
-- 2. PRIORITIES (Required for issues)
-- ============================================
INSERT INTO priorities (id, name, display_order) VALUES
(1, 'Low', 1),
(2, 'Medium', 2),
(3, 'High', 3),
(4, 'Critical', 4)
ON CONFLICT (id) DO NOTHING;

-- Reset sequence for priorities
SELECT setval('priorities_id_seq', (SELECT MAX(id) FROM priorities));

-- ============================================
-- 3. TAGS (Optional but useful)
-- ============================================
INSERT INTO tags (id, name, color, display_order) VALUES
(1, 'bug', '#ef4444', 1),
(2, 'feature', '#22c55e', 2),
(3, 'enhancement', '#3b82f6', 3),
(4, 'documentation', '#8b5cf6', 4),
(5, 'ui', '#06b6d4', 5),
(6, 'backend', '#f59e0b', 6),
(7, 'frontend', '#ec4899', 7),
(8, 'security', '#dc2626', 8),
(9, 'performance', '#10b981', 9),
(10, 'testing', '#6366f1', 10)
ON CONFLICT (id) DO NOTHING;

-- Reset sequence for tags
SELECT setval('tags_id_seq', (SELECT MAX(id) FROM tags));

-- ============================================
-- 4. SAMPLE ADMIN USER (Optional)
-- ============================================
-- Password: admin123 (hashed with bcrypt)
-- You should change this password after first login!
INSERT INTO users (id, name, email, password_hash, role) VALUES
(1, 'Admin User', 'admin@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYqVr/1jrku', 'admin')
ON CONFLICT (email) DO NOTHING;

-- Reset sequence for users
SELECT setval('users_id_seq', (SELECT MAX(id) FROM users));

-- ============================================
-- 5. SAMPLE REGULAR USER (Optional)
-- ============================================
-- Password: user123 (hashed with bcrypt)
INSERT INTO users (id, name, email, password_hash, role) VALUES
(2, 'Test User', 'user@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYqVr/1jrku', 'user')
ON CONFLICT (email) DO NOTHING;

-- Reset sequence for users (again, after second user)
SELECT setval('users_id_seq', (SELECT MAX(id) FROM users));

-- ============================================
-- VERIFICATION QUERIES
-- ============================================
-- Run these to verify the data was inserted:

-- SELECT * FROM statuses ORDER BY display_order;
-- SELECT * FROM priorities ORDER BY display_order;
-- SELECT * FROM tags ORDER BY display_order;
-- SELECT id, name, email, role FROM users;


