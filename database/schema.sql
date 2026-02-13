-- Kronos Database Schema
-- UK Public Data Database for AI Email Campaigns

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Main entity table
CREATE TABLE entities (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(500) NOT NULL,
    category VARCHAR(100) NOT NULL,
    subcategory VARCHAR(100),
    address_line1 VARCHAR(500),
    address_line2 VARCHAR(500),
    city VARCHAR(200),
    county VARCHAR(200),
    postcode VARCHAR(20),
    country VARCHAR(100) DEFAULT 'UK',
    website VARCHAR(500),
    email VARCHAR(500),
    phone VARCHAR(100),
    source_url VARCHAR(1000),
    source_name VARCHAR(200),
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Contacts table (linked to entities)
CREATE TABLE contacts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    entity_id UUID REFERENCES entities(id) ON DELETE CASCADE,
    name VARCHAR(500),
    title VARCHAR(500),
    department VARCHAR(500),
    email VARCHAR(500),
    phone VARCHAR(100),
    role VARCHAR(200),
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT NOW()
);

-- Categories reference
CREATE TABLE categories (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    priority INTEGER DEFAULT 0
);

-- Insert categories
INSERT INTO categories (name, description, priority) VALUES
('education', 'Schools, colleges, universities', 1),
('healthcare', 'Hospitals, NHS trusts, healthcare providers', 2),
('public_buildings', 'Government buildings, councils, libraries', 3),
('vc', 'Venture capital and angel investors', 4),
('charities', 'Charities and NGOs', 5),
('politics', 'MPs, lords, mayors, councillors', 6),
('media', 'Newspapers, media outlets', 7),
('grants', 'Grant bodies and funding organizations', 8),
('businesses', 'Top UK companies with CSR/ESG depts', 9);

-- Indexes for performance
CREATE INDEX idx_entities_category ON entities(category);
CREATE INDEX idx_entities_city ON entities(city);
CREATE INDEX idx_entities_postcode ON entities(postcode);
CREATE INDEX idx_entities_name ON entities(name);
CREATE INDEX idx_contacts_entity_id ON contacts(entity_id);
CREATE INDEX idx_contacts_email ON contacts(email);

-- Full text search (if using PostgreSQL)
-- CREATE EXTENSION IF NOT EXISTS pg_trgm;
-- CREATE INDEX idx_entities_name_fts ON entities USING gin(name gin_trgm_ops);
-- CREATE INDEX idx_entities_metadata_fts ON entities USING gin(metadata jsonb_path_ops);

-- Source tracking
CREATE TABLE data_sources (
    id SERIAL PRIMARY KEY,
    source_name VARCHAR(200) NOT NULL,
    source_url VARCHAR(1000),
    api_available BOOLEAN DEFAULT FALSE,
    data_format VARCHAR(100),
    last_scraped TIMESTAMP,
    record_count INTEGER DEFAULT 0
);

-- Scraping/collection log
CREATE TABLE collection_log (
    id SERIAL PRIMARY KEY,
    category VARCHAR(100),
    source_name VARCHAR(200),
    action VARCHAR(100),
    records_collected INTEGER,
    started_at TIMESTAMP DEFAULT NOW(),
    completed_at TIMESTAMP,
    status VARCHAR(50),
    notes TEXT
);
