create extension if not exists pgcrypto;

create table if not exists users (
  id uuid primary key default gen_random_uuid(),
  email varchar(255) unique not null,
  password_hash varchar(255) not null,
  created_at timestamptz not null default now()
);

create table if not exists refresh_tokens (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references users(id) on delete cascade,
  token_hash varchar(255) unique not null,
  expires_at timestamptz not null,
  revoked boolean not null default false,
  created_at timestamptz not null default now()
);

create table if not exists conversations (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references users(id) on delete cascade,
  title varchar(500) not null,
  model varchar(100) not null,
  system_prompt text,
  metadata jsonb not null default '{}'::jsonb,
  is_archived boolean not null default false,
  is_deleted boolean not null default false,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists messages (
  id uuid primary key default gen_random_uuid(),
  conversation_id uuid not null references conversations(id) on delete cascade,
  role varchar(20) not null check (role in ('user','assistant','system')),
  content text not null,
  token_count int not null default 0,
  model varchar(100),
  finish_reason varchar(50),
  latency_ms int,
  metadata jsonb not null default '{}'::jsonb,
  estimated_cost_usd numeric(12,8) not null default 0,
  created_at timestamptz not null default now()
);

create table if not exists api_keys (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references users(id) on delete cascade,
  key_hash varchar(255) unique not null,
  key_prefix varchar(20) not null,
  name varchar(100) not null,
  scopes text[] not null default '{}',
  last_used_at timestamptz,
  expires_at timestamptz,
  is_active boolean not null default true,
  created_at timestamptz not null default now()
);
