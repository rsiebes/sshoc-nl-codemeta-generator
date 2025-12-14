"""
Codemeta 3.1 Property Modules

This package contains individual modules for each Codemeta 3.1 property.
Each module handles extraction, validation, and conversion of a specific property.
"""

# Import implemented modules
from .name import NameMetadata
from .description import DescriptionMetadata
from .url import UrlMetadata
from .version import VersionMetadata
from .code_repository import CodeRepositoryMetadata
from .license import LicenseMetadata

# Import placeholder modules
from .keywords import KeywordsMetadata
from .application_category import ApplicationCategoryMetadata
from .application_sub_category import ApplicationSubCategoryMetadata
from .author import AuthorMetadata
from .contributor import ContributorMetadata
from .maintainer import MaintainerMetadata
from .copyright_holder import CopyrightHolderMetadata
from .copyright_year import CopyrightYearMetadata
from .funder import FunderMetadata
from .sponsor import SponsorMetadata
from .publisher import PublisherMetadata
from .editor import EditorMetadata
from .producer import ProducerMetadata
from .provider import ProviderMetadata
from .date_created import DateCreatedMetadata
from .date_modified import DateModifiedMetadata
from .date_published import DatePublishedMetadata
from .embargo_end_date import EmbargoEndDateMetadata
from .programming_language import ProgrammingLanguageMetadata
from .operating_system import OperatingSystemMetadata
from .runtime_platform import RuntimePlatformMetadata
from .software_requirements import SoftwareRequirementsMetadata
from .software_suggestions import SoftwareSuggestionsMetadata
from .processor_requirements import ProcessorRequirementsMetadata
from .memory_requirements import MemoryRequirementsMetadata
from .storage_requirements import StorageRequirementsMetadata
from .readme import ReadmeMetadata
from .software_help import SoftwareHelpMetadata
from .release_notes import ReleaseNotesMetadata
from .build_instructions import BuildInstructionsMetadata
from .issue_tracker import IssueTrackerMetadata
from .reference_publication import ReferencePublicationMetadata
from .development_status import DevelopmentStatusMetadata
from .continuous_integration import ContinuousIntegrationMetadata
from .review import ReviewMetadata
from .download_url import DownloadUrlMetadata
from .install_url import InstallUrlMetadata
from .related_link import RelatedLinkMetadata
from .same_as import SameAsMetadata
from .is_part_of import IsPartOfMetadata
from .has_part import HasPartMetadata
from .supporting_data import SupportingDataMetadata
from .has_source_code import HasSourceCodeMetadata
from .is_source_code_of import IsSourceCodeOfMetadata
from .identifier import IdentifierMetadata
from .permissions import PermissionsMetadata
from .is_accessible_for_free import IsAccessibleForFreeMetadata
from .funding import FundingMetadata

__all__ = [
    'NameMetadata',
    'DescriptionMetadata',
    'UrlMetadata',
    'VersionMetadata',
    'CodeRepositoryMetadata',
    'LicenseMetadata',
    'KeywordsMetadata',
    'ApplicationCategoryMetadata',
    'ApplicationSubCategoryMetadata',
    'AuthorMetadata',
    'ContributorMetadata',
    'MaintainerMetadata',
    'CopyrightHolderMetadata',
    'CopyrightYearMetadata',
    'FunderMetadata',
    'SponsorMetadata',
    'PublisherMetadata',
    'EditorMetadata',
    'ProducerMetadata',
    'ProviderMetadata',
    'DateCreatedMetadata',
    'DateModifiedMetadata',
    'DatePublishedMetadata',
    'EmbargoEndDateMetadata',
    'ProgrammingLanguageMetadata',
    'OperatingSystemMetadata',
    'RuntimePlatformMetadata',
    'SoftwareRequirementsMetadata',
    'SoftwareSuggestionsMetadata',
    'ProcessorRequirementsMetadata',
    'MemoryRequirementsMetadata',
    'StorageRequirementsMetadata',
    'ReadmeMetadata',
    'SoftwareHelpMetadata',
    'ReleaseNotesMetadata',
    'BuildInstructionsMetadata',
    'IssueTrackerMetadata',
    'ReferencePublicationMetadata',
    'DevelopmentStatusMetadata',
    'ContinuousIntegrationMetadata',
    'ReviewMetadata',
    'DownloadUrlMetadata',
    'InstallUrlMetadata',
    'RelatedLinkMetadata',
    'SameAsMetadata',
    'IsPartOfMetadata',
    'HasPartMetadata',
    'SupportingDataMetadata',
    'HasSourceCodeMetadata',
    'IsSourceCodeOfMetadata',
    'IdentifierMetadata',
    'PermissionsMetadata',
    'IsAccessibleForFreeMetadata',
    'FundingMetadata',
]
