
# Implementing CC BY-NC License in Riddler

This document provides comprehensive instructions for implementing the Creative Commons Attribution-NonCommercial (CC BY-NC) 4.0 International License in your Riddler project.

## Why CC BY-NC?

The CC BY-NC license allows others to:
- Share, copy, and redistribute your code
- Adapt and build upon your code
- Maintain attribution to you as the original creator

While prohibiting:
- Commercial use without your explicit permission

This preserves your intellectual property rights while still allowing for open-source collaboration.

## Implementation Steps

### 1. Replace the LICENSE File

Replace the entire content of your `LICENSE` file with the official CC BY-NC text:

```
Creative Commons Attribution-NonCommercial 4.0 International License

Copyright (c) 2024 Riddler

This work is licensed under the Creative Commons Attribution-NonCommercial 4.0
International License.

To view a copy of this license, visit:
https://creativecommons.org/licenses/by-nc/4.0/legalcode

or send a letter to:
Creative Commons, PO Box 1866, Mountain View, CA 94042, USA.

===============================================================================

Attribution — You must give appropriate credit, provide a link to the license,
and indicate if changes were made. You may do so in any reasonable manner, but
not in any way that suggests the licensor endorses you or your use.

NonCommercial — You may not use the material for commercial purposes.

No additional restrictions — You may not apply legal terms or technological
measures that legally restrict others from doing anything the license permits.

===============================================================================

The full license text can be found at:
https://creativecommons.org/licenses/by-nc/4.0/legalcode
```

### 2. Update the README File

Update line 5 in `README.md` to show the new license badge:

```markdown
![License](https://img.shields.io/badge/License-CC%20BY--NC%204.0-lightgrey)
```

And update the license section (line 65) to:

```markdown
## 📝 License

This work is licensed under a [Creative Commons Attribution-NonCommercial 4.0 International License](LICENSE). Copyright (c) 2024 Riddler.
```

### 3. Update CONTRIBUTING.md

Change the license section (line 68) in `CONTRIBUTING.md` to:

```markdown
## License

By contributing, you agree that your contributions will be licensed under the project's Creative Commons Attribution-NonCommercial 4.0 International License. All intellectual property rights remain with the original author. Contributors retain copyright to their contributions but grant the project the rights to use those contributions under the CC BY-NC license.
```

### 4. Add License Headers to Key Source Files

Add this header to all main Python files (like core modules, services, and main.py):

```python
"""
Riddler - AI-Powered Riddle Generation System

This file is part of Riddler.
Copyright (c) 2024 Riddler

This work is licensed under the Creative Commons Attribution-NonCommercial 4.0
International License. To view a copy of this license, visit:
https://creativecommons.org/licenses/by-nc/4.0/
"""
```

### 5. Create a LICENSE.md File

Create a new file called `LICENSE.md` with this content:

```markdown
# License Information

## Riddler License: CC BY-NC 4.0

This work is licensed under a [Creative Commons Attribution-NonCommercial 4.0 International License](https://creativecommons.org/licenses/by-nc/4.0/).

### What this means:

#### You are free to:
- **Share** — copy and redistribute the material in any medium or format
- **Adapt** — remix, transform, and build upon the material

#### Under the following terms:
- **Attribution** — You must give appropriate credit, provide a link to the license, and indicate if changes were made. You may do so in any reasonable manner, but not in any way that suggests the licensor endorses you or your use.
- **NonCommercial** — You may not use the material for commercial purposes.

### Commercial Use

For commercial licensing options, please contact the copyright holder.

### Attribution Example

```
Based on Riddler (https://github.com/your-username/riddler) by [Your Name], 
licensed under CC BY-NC 4.0.
```

## Copyright

Copyright (c) 2024 Riddler
```

### 6. Add a Usage Permissions Section to docs.md

Add this section to your `docs.md` file:

```markdown
## Usage Permissions

Riddler is licensed under the Creative Commons Attribution-NonCommercial 4.0 International License.

### Permitted Uses
- Educational projects
- Personal use
- Research
- Non-profit organizations
- Extending the codebase for non-commercial applications

### Prohibited Uses
- Commercial applications without explicit permission
- Selling or licensing the software
- Using the software to generate content for commercial purposes
- Incorporating the code into commercial products

### Getting Permission for Commercial Use
For commercial licensing inquiries, please contact [your contact information].
```

### 7. Update CHANGELOG.md

Add a new entry to your `CHANGELOG.md`:

```markdown
## [Unreleased]

### Changed
- Updated project license from MIT to Creative Commons Attribution-NonCommercial 4.0 International License
```

### 8. Create a Contributor License Agreement (Optional but Recommended)

Create a file called `CLA.md`:

```markdown
# Contributor License Agreement

By making a contribution to this project, I certify that:

1. I am the copyright owner of the contribution or have appropriate rights to contribute the content.

2. I grant the project maintainer a perpetual, worldwide, non-exclusive, no-charge, royalty-free, irrevocable license to use, reproduce, prepare derivative works of, publicly display, publicly perform, sublicense, and distribute my contributions and derivative works.

3. I understand that my contributions will be licensed under the project's Creative Commons Attribution-NonCommercial 4.0 International License.

4. I understand that the project and my contributions are provided "AS IS" without warranty of any kind.
```

## Important Considerations

### 1. Handle Previous Contributions

If you've received contributions under the MIT license:
- Consider reaching out to past contributors to inform them of the license change
- Get their explicit consent to relicense their contributions
- Document this consent for your records

### 2. Review Third-Party Dependencies

- Check all dependencies to ensure they are compatible with CC BY-NC
- Be particularly cautious of GPL-licensed dependencies, which may conflict

### 3. Communicating the Change

If this is a public repository:
- Create a clear announcement of the license change
- Tag a final release under the MIT license
- Start a new version under the CC BY-NC license

### 4. Versioning Recommendation

- Consider tagging the license change with a major version increment (e.g., v1.0.0 → v2.0.0)
- Document the license change prominently in your release notes

## Final Steps Checklist

- [ ] Replace LICENSE file
- [ ] Update README.md
- [ ] Update CONTRIBUTING.md
- [ ] Add license headers to source files
- [ ] Create LICENSE.md
- [ ] Update docs.md
- [ ] Update CHANGELOG.md
- [ ] Create CLA.md (optional)
- [ ] Contact previous contributors (if applicable)
- [ ] Review dependencies
- [ ] Make public announcement (if applicable)
- [ ] Tag new version

By following these steps, you will have properly implemented the CC BY-NC license, protecting your intellectual property rights while still maintaining the collaborative benefits of open source.
