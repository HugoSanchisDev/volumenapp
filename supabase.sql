-- ============================================================
--  Volumen: tablas y seguridad para Supabase
--  Pégalo entero en Supabase > SQL Editor > New query > Run
-- ============================================================

-- 1) Tabla con todos tus datos (perfil, pesos, check-ins, plan...)
create table if not exists public.app_state (
  user_id    uuid primary key references auth.users(id) on delete cascade,
  data       jsonb not null,
  updated_at timestamptz not null default now()
);

-- 2) Seguridad: cada usuario solo puede leer y escribir su propia fila
alter table public.app_state enable row level security;

create policy "Leer mis datos"   on public.app_state for select to authenticated using ((select auth.uid()) = user_id);
create policy "Crear mis datos"  on public.app_state for insert to authenticated with check ((select auth.uid()) = user_id);
create policy "Editar mis datos" on public.app_state for update to authenticated using ((select auth.uid()) = user_id) with check ((select auth.uid()) = user_id);
create policy "Borrar mis datos" on public.app_state for delete to authenticated using ((select auth.uid()) = user_id);

-- 3) Carpeta PRIVADA para las fotos de progreso
insert into storage.buckets (id, name, public)
values ('fotos', 'fotos', false)
on conflict (id) do nothing;

-- 4) Cada usuario solo accede a las fotos de su propia carpeta (fotos/<su id>/...)
create policy "Ver mis fotos"    on storage.objects for select to authenticated
  using (bucket_id = 'fotos' and (storage.foldername(name))[1] = (select auth.uid())::text);
create policy "Subir mis fotos"  on storage.objects for insert to authenticated
  with check (bucket_id = 'fotos' and (storage.foldername(name))[1] = (select auth.uid())::text);
create policy "Borrar mis fotos" on storage.objects for delete to authenticated
  using (bucket_id = 'fotos' and (storage.foldername(name))[1] = (select auth.uid())::text);
