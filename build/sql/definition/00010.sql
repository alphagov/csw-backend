INSERT INTO public.status (id, status_name, description)
VALUES
(4, 'Excepted', 'The user has recorded an exception to stop this resource failing')
ON CONFLICT DO NOTHING;