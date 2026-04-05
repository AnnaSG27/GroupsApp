-- ============================================
-- PostgreSQL DDL Script
-- ============================================

-- Crear esquema (opcional)
CREATE SCHEMA IF NOT EXISTS mydb;
SET search_path TO mydb;

-- ============================================
-- Tabla: users
-- ============================================
CREATE TABLE IF NOT EXISTS users (
    id_user SERIAL PRIMARY KEY,
    username VARCHAR(150) NOT NULL,
    password VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL,
    name VARCHAR(100) NOT NULL,
    is_active BOOLEAN NOT NULL
);

-- ============================================
-- Tabla: groups
-- ============================================
CREATE TABLE IF NOT EXISTS group (
    id_group SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description VARCHAR(255) NOT NULL,
    created_by INT NOT NULL,
    created_at TIMESTAMP NOT NULL,
    is_direct BOOLEAN,

    CONSTRAINT fk_group_user
        FOREIGN KEY (created_by)
        REFERENCES users (id_user)
        ON DELETE NO ACTION
        ON UPDATE NO ACTION
);

-- ============================================
-- Tabla: group_members
-- ============================================
CREATE TABLE IF NOT EXISTS group_members (
    id_group INT NOT NULL,
    id_member INT NOT NULL,
    role VARCHAR(45) NOT NULL,
    joined_at TIMESTAMP NOT NULL,

    PRIMARY KEY (id_group, id_member),

    CONSTRAINT fk_groupmember_group
        FOREIGN KEY (id_group)
        REFERENCES group (id_group)
        ON DELETE NO ACTION
        ON UPDATE NO ACTION,

    CONSTRAINT fk_groupmember_user
        FOREIGN KEY (id_member)
        REFERENCES users (id_user)
        ON DELETE NO ACTION
        ON UPDATE NO ACTION
);