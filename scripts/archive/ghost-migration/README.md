# Ghost migration scripts

These scripts record how the blog moved from Ghost to Astro. They are unmaintained, and no recipe runs them.

Decision R9 keeps the scripts as a record of the migration. The Ghost export is unavailable, so the 28 uncertain post dates remain as they are. [Business case, section 3](../../../plan/00-business-case.md#s3)

| Script                   | Role in the migration                                                               |
| ------------------------ | ----------------------------------------------------------------------------------- |
| `import_ghost_posts.py`  | Imported selected Ghost posts, copied referenced images, and rewrote S3 image paths |
| `convert_frontmatter.py` | Converted old post metadata to the AstroPaper frontmatter schema                    |
| `normalize-tags.py`      | Normalized tag names to kebab case and formatted them as YAML lists                 |
| `rename_to_kebab.py`     | Renamed image files to kebab case and updated Markdown references                   |
| `analyze_images.py`      | Reported duplicate and unused images in the legacy image collection                 |
