# Codemeta 3.1 Properties - Complete List

This document lists all properties defined in the Codemeta 3.1 schema.

## Software/Source Code Properties (68 total)

### Core Metadata
1. **name** - The name of the software ✅ *Implemented*
2. **description** - A description of the software ✅ *Implemented*
3. **version** - The version of the software ✅ *Implemented*
4. **identifier** - A unique identifier for the software (DOI, etc.)
5. **url** - The URL of the software website ✅ *Implemented*
6. **codeRepository** - Link to the repository where the code is located ✅ *Implemented*
7. **license** - The license under which the software is distributed ✅ *Implemented*

### Categories and Keywords
8. **keywords** - Keywords or tags describing the software
9. **applicationCategory** - Type of software application
10. **applicationSubCategory** - Subcategory of the software application

### People and Organizations
11. **author** - The author(s) of the software
12. **contributor** - Contributor(s) to the software
13. **maintainer** - The maintainer(s) of the software
14. **copyrightHolder** - The copyright holder(s)
15. **copyrightYear** - The year of copyright
16. **funder** - The funder(s) of the software
17. **sponsor** - The sponsor(s) of the software
18. **publisher** - The publisher of the software
19. **editor** - The editor(s) of the software
20. **producer** - The producer(s) of the software
21. **provider** - The provider(s) of the software

### Dates
22. **dateCreated** - Date when the software was created
23. **dateModified** - Date when the software was last modified
24. **datePublished** - Date when the software was published
25. **embargoEndDate** - Date when embargo ends
26. **startDate** - Start date
27. **endDate** - End date

### Technical Requirements
28. **programmingLanguage** - Programming language(s) used
29. **operatingSystem** - Operating system(s) supported
30. **runtimePlatform** - Runtime platform(s) required
31. **softwareRequirements** - Software dependencies
32. **softwareSuggestions** - Suggested software
33. **processorRequirements** - Processor requirements
34. **memoryRequirements** - Memory requirements
35. **storageRequirements** - Storage requirements
36. **targetProduct** - Target product

### Documentation and Help
37. **readme** - README content or URL
38. **softwareHelp** - Help documentation URL
39. **releaseNotes** - Release notes URL
40. **buildInstructions** - Build instructions URL
41. **issueTracker** - Issue tracker URL
42. **referencePublication** - Reference publication(s)

### Development
43. **developmentStatus** - Development status (e.g., active, inactive)
44. **continuousIntegration** - Continuous integration URL
45. **review** - Review(s) of the software
46. **reviewAspect** - Aspect of the review
47. **reviewBody** - Body of the review

### URLs and Links
48. **downloadUrl** - Download URL
49. **installUrl** - Installation URL
50. **relatedLink** - Related link(s)
51. **sameAs** - Same as URL(s) (alternative identifiers)
52. **hasSourceCode** - Source code URL
53. **isSourceCodeOf** - Software this is source code of

### Relationships
54. **isPartOf** - Parent software or collection
55. **hasPart** - Component(s) of the software
56. **supportingData** - Supporting data
57. **citation** - Citation for the software

### Funding
58. **funding** - Funding information

### Access and Permissions
59. **permissions** - Permissions
60. **isAccessibleForFree** - Whether accessible for free

### File Information
61. **encoding** - Encoding format
62. **fileFormat** - File format
63. **fileSize** - File size

### Other
64. **softwareVersion** - Software version (alternative to version)
65. **id** - Identifier (JSON-LD @id)
66. **type** - Type (JSON-LD @type)
67. **codemeta** - Codemeta namespace
68. **schema** - Schema.org namespace

## Person/Organization Properties (7 total)

These are nested properties used within Person and Organization objects:

1. **givenName** - Given name (first name)
2. **familyName** - Family name (last name)
3. **email** - Email address
4. **affiliation** - Affiliation (organization)
5. **address** - Physical address
6. **roleName** - Role name
7. **position** - Position

## Types (8 total)

1. **SoftwareSourceCode** - Main type for software
2. **SoftwareApplication** - Type for applications
3. **Person** - Type for person objects
4. **Organization** - Type for organization objects
5. **Role** - Type for role objects
6. **Review** - Type for review objects
7. **Text** - Type for text objects
8. **URL** - Type for URL objects

## Implementation Status

### ✅ Fully Implemented (6)
- name
- description
- url
- version
- codeRepository
- license

### 🔄 Placeholder Created (48)
All remaining main software properties have placeholder modules ready for implementation.

### 📝 To Be Implemented (14)
Person/Organization nested properties and some specialized properties.

## Priority for Implementation

### High Priority (Essential)
1. keywords
2. programmingLanguage
3. author
4. dateCreated
5. dateModified
6. readme
7. issueTracker

### Medium Priority (Important)
8. contributor
9. maintainer
10. operatingSystem
11. softwareRequirements
12. developmentStatus
13. downloadUrl
14. identifier

### Low Priority (Optional)
15. All remaining properties

## Notes

- Properties marked with ✅ are fully implemented with tests
- Properties with 🔄 have placeholder modules ready for implementation
- Person and Organization properties are nested within main properties like author, contributor, etc.
- Some properties like `id`, `type`, `schema`, `codemeta` are JSON-LD structural properties
