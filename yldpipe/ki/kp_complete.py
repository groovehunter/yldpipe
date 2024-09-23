# Build the new group structure
builder = KeepassGroupBuilder('group_structure.yaml')
builder.build_group_structure()
# Migrate entries from the legacy database
migrator = LegacyToNewDatabaseMigrator(legacy_db, new_db, 'group_mapping.yaml')
migrator.migrate()
# Validate and normalize entries
validator = EntryValidator('validation_config.yaml')
normalizer = EntryNormalizer('normalization_config.yaml')

for entry in new_db.entries:
    if validator.validate(entry):
        normalizer.normalize(entry)
