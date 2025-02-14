# Database Schema Documentation

## Overview

This document provides an overview of the PostgreSQL database schema,
including tables, sequences, indexes, and constraints.

## Database Information

- **PostgreSQL Version:** 17.2
- **Dump Date:** 2025-02-14

## Tables and Structure

### 1. `apikeys`

Stores API keys assigned to users allow better control api usage.

- **Columns:**
    - `id` (integer, primary key)
    - `api_key` (varchar, unique) , api key assigned to user
    - `expires_at` (timestamp, nullable)
    - `is_active` (boolean, not null)
    - `created_at` (timestamp)
    - `updated_at` (timestamp)
    - `user_id` (integer, foreign key referencing `user.id`)

### 2. `permissions`

Defines different permissions available in the system.

- **Columns:**
    - `id` (integer, primary key)
    - `permission_name` (varchar, unique, not null) e.g. api_generate_token
    - `descriptions` (varchar, not null) e.g. Allows the user or application
      to generate token
    - `created_at` (timestamp)

### 3. `roles`

Stores user roles.

- **Columns:**
    - `id` (integer, primary key)
    - `role_name` (varchar, unique, not null) e.g. api_user, admin
    - `created_at` (timestamp)

### 4. `rolepermissions`

Many-to-many mapping between `roles` and `permissions`.

- **Columns:**
    - `role_id` (integer, foreign key referencing `roles.id`)
    - `permission_id` (integer, foreign key referencing `permissions.id`)
    - `granted_at` (timestamp)

### 5. `user`

Stores user account information both regular and API users.

- **Columns:**
    - `id` (integer, primary key)
    - `username` (varchar, unique, not null)
    - `email` (varchar, unique, not null)
    - `password_hash` (varchar, not null)
    - `is_active` (boolean, not null)
    - `is_disabled` (boolean, not null)
    - `created_at` (timestamp)
    - `updated_at` (timestamp)

### 6. `userprofile`

Additional user profile details to maintain normalization between user table.

- **Columns:**
    - `id` (integer, primary key)
    - `first_name` (varchar, not null)
    - `last_name` (varchar, not null)
    - `phone_number` (varchar, nullable)
    - `address` (varchar, nullable)
    - `birth_date` (date, not null)
    - `bio` (varchar, nullable)
    - `created_at` (timestamp)
    - `updated_at` (timestamp)
    - `user_id` (integer, foreign key referencing `user.id`)

### 7. `userroles`

Many-to-many mapping between `users` and `roles`.

- **Columns:**
    - `user_id` (integer, foreign key referencing `user.id`)
    - `role_id` (integer, foreign key referencing `roles.id`) e.g.
    - `created_at` (timestamp)

## Sequences

Each table with an `id` column has an associated sequence to ensure unique
values.

- `apikeys_id_seq`
- `permissions_id_seq`
- `roles_id_seq`
- `user_id_seq`
- `userprofile_id_seq`

## Indexes

- Unique indexes on `email` and `username` in the `user` table.
- Unique indexes on `permission_name` and `role_name`.
- Index on `first_name` in the `userprofile` table.

## Constraints

- Primary keys for each table.
- Foreign key constraints ensure data integrity between `users`, `roles`, and
  `permissions`.

