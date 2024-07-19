INSERT INTO public.users (email, password, full_name) VALUES ('user@test.test', 'password', 'Test User');
WITH last_user_id AS (
    SELECT lastval() AS id
)
INSERT INTO public.bank_accounts (account_id, user_id, balance) SELECT 0, id, 0 FROM last_user_id;
INSERT INTO public.admins (email, password, full_name) VALUES ('admin@test.test', 'password', 'Test Admin');