"""
Application Sub Category Property Module

This module extracts domain-specific terms from repository metadata
to create meaningful applicationSubCategory values.
"""

import re
from typing import Optional
from src.base_metadata import BaseMetadata
from src.execution_profiler import profile


class ApplicationSubCategoryMetadata(BaseMetadata):
    """Extracts domain-specific terms as applicationSubCategory."""

    CODEMETA_PROPERTY = 'applicationSubCategory'
    CODEMETA_TYPE = 'schema:Text'
    REQUIRED = False

    def extract(self) -> None:
        """
        Extract applicationSubCategory by identifying domain-specific terms
        from repository metadata (description, README, topics, keywords).
        """
        # Get repository metadata
        description = self._get_value('description') or ''
        readme_content = self._get_value('readme_content') or ''
        topics = self._get_value('topics') or []
        keywords = self._get_value('keywords') or []
        programming_languages = self._get_value('programmingLanguage') or []

        # Extract domain-specific terms
        domain_terms = self._extract_domain_terms(
            description, readme_content, topics, keywords, programming_languages
        )

        # Create subcategory from domain terms
        if domain_terms:
            # Concatenate the most relevant terms
            self.metadata = ', '.join(domain_terms[:5])  # Top 5 terms
        else:
            self.metadata = None

    def _extract_domain_terms(self, description: str, readme_content: str, 
                             topics: list, keywords: list, languages: list) -> list:
        """
        Extract domain-specific terms from repository metadata.

        Args:
            description: Repository description
            readme_content: README content
            topics: Repository topics
            keywords: Repository keywords
            languages: Programming languages

        Returns:
            List of domain-specific terms, sorted by relevance
        """
        terms = {}

        # 1. Use topics directly (highest priority - explicitly set by maintainers)
        for topic in topics:
            if topic and len(topic) > 2:
                terms[topic.lower()] = 3.0  # High weight

        # 2. Extract from description
        if description:
            desc_terms = self._extract_terms_from_text(description)
            for term in desc_terms:
                current_weight = terms.get(term, 0)
                terms[term] = max(current_weight, 2.0)  # Medium-high weight

        # 3. Extract from README
        if readme_content:
            readme_terms = self._extract_terms_from_text(readme_content)
            for term in readme_terms:
                current_weight = terms.get(term, 0)
                terms[term] = max(current_weight, 1.5)  # Medium weight

        # 4. Use keywords
        for keyword in keywords:
            if keyword and len(keyword) > 2:
                current_weight = terms.get(keyword.lower(), 0)
                terms[keyword.lower()] = max(current_weight, 1.0)  # Low-medium weight

        # 5. Include programming languages
        for lang in languages:
            if lang and len(lang) > 2:
                current_weight = terms.get(lang.lower(), 0)
                terms[lang.lower()] = max(current_weight, 1.2)  # Medium weight

        # Sort by weight and return unique terms
        sorted_terms = sorted(terms.items(), key=lambda x: x[1], reverse=True)
        return [term[0] for term in sorted_terms if term[0] and len(term[0]) > 2]

    def _extract_terms_from_text(self, text: str) -> list:
        """
        Extract meaningful terms from text using simple NLP techniques.

        Args:
            text: Text to extract terms from

        Returns:
            List of extracted terms
        """
        terms = []

        # Remove markdown formatting
        text = re.sub(r'[#*_`\[\]()]', ' ', text)

        # Extract capitalized words (likely proper nouns/technical terms)
        capitalized = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', text)
        terms.extend([t.lower() for t in capitalized if len(t) > 3])

        # Extract common technical terms
        technical_keywords = [
            'framework', 'library', 'tool', 'platform', 'engine', 'system', 'service',
            'application', 'software', 'package', 'module', 'plugin', 'extension',
            'middleware', 'protocol', 'standard', 'format', 'language', 'compiler',
            'interpreter', 'runtime', 'environment', 'container', 'orchestration',
            'automation', 'monitoring', 'logging', 'testing', 'build', 'deployment',
            'infrastructure', 'cloud', 'distributed', 'parallel', 'concurrent',
            'api', 'rest', 'graphql', 'grpc', 'soap', 'websocket', 'mqtt',
            'database', 'cache', 'queue', 'stream', 'search', 'analytics',
            'machine-learning', 'deep-learning', 'neural-network', 'ai', 'nlp', 'cv',
            'web', 'mobile', 'desktop', 'cli', 'gui', 'ui', 'ux', 'frontend', 'backend',
            'fullstack', 'microservices', 'serverless', 'lambda', 'function',
            'docker', 'kubernetes', 'terraform', 'ansible', 'jenkins', 'gitlab',
            'github', 'git', 'svn', 'mercurial', 'perforce', 'clearcase',
            'python', 'javascript', 'typescript', 'java', 'csharp', 'cpp', 'rust',
            'go', 'ruby', 'php', 'swift', 'kotlin', 'scala', 'clojure', 'haskell',
            'elixir', 'erlang', 'r', 'matlab', 'julia', 'perl', 'lua', 'groovy',
            'sql', 'nosql', 'mongodb', 'postgresql', 'mysql', 'sqlite', 'cassandra',
            'redis', 'elasticsearch', 'kafka', 'rabbitmq', 'activemq', 'zeromq',
            'react', 'vue', 'angular', 'svelte', 'ember', 'backbone', 'knockout',
            'jquery', 'bootstrap', 'tailwind', 'material', 'ant-design', 'semantic-ui',
            'express', 'fastapi', 'django', 'flask', 'rails', 'sinatra', 'spring',
            'quarkus', 'micronaut', 'grails', 'play', 'akka', 'lagom', 'vert.x',
            'node', 'deno', 'bun', 'electron', 'tauri', 'flutter', 'react-native',
            'xamarin', 'ionic', 'cordova', 'phonegap', 'nativescript', 'weex',
            'unity', 'unreal', 'godot', 'pygame', 'phaser', 'babylon', 'three',
            'cesium', 'leaflet', 'mapbox', 'd3', 'plotly', 'bokeh', 'matplotlib',
            'seaborn', 'ggplot', 'lattice', 'dplyr', 'tidyverse', 'shiny', 'rmarkdown',
            'jupyter', 'ipython', 'anaconda', 'miniconda', 'pip', 'conda', 'npm',
            'yarn', 'pnpm', 'bower', 'maven', 'gradle', 'sbt', 'leiningen', 'cargo',
            'rustup', 'nix', 'guix', 'homebrew', 'apt', 'yum', 'pacman', 'emerge',
            'openbsd', 'freebsd', 'netbsd', 'dragonfly', 'illumos', 'solaris',
            'linux', 'unix', 'windows', 'macos', 'ios', 'android', 'chromeos',
            'webos', 'tizen', 'sailfish', 'ubuntu', 'debian', 'fedora', 'centos',
            'rhel', 'sles', 'opensuse', 'arch', 'gentoo', 'alpine', 'busybox',
            'docker', 'podman', 'containerd', 'rkt', 'cri-o', 'lxc', 'lxd',
            'kvm', 'xen', 'hyperv', 'vmware', 'virtualbox', 'qemu', 'bochs',
            'dosbox', 'wine', 'proton', 'crossover', 'parallels', 'fusion',
            'aws', 'azure', 'gcp', 'ibm', 'oracle', 'alibaba', 'digitalocean',
            'linode', 'vultr', 'hetzner', 'ovh', 'scaleway', 'upcloud', 'packet',
            'equinix', 'rackspace', 'softlayer', 'joyent', 'triton', 'smartos',
            'openstack', 'eucalyptus', 'cloudstack', 'opennebula', 'proxmox',
            'vmware', 'hyper-v', 'citrix', 'xenserver', 'nutanix', 'simplivity',
            'vsan', 'vvols', 'srdf', 'snapvault', 'snapmirror', 'replication',
            'backup', 'recovery', 'disaster', 'failover', 'failback', 'switchover',
            'clustering', 'ha', 'high-availability', 'load-balancing', 'failover',
            'redundancy', 'replication', 'synchronization', 'asynchronous', 'async',
            'sync', 'eventual-consistency', 'strong-consistency', 'causal-consistency',
            'session-consistency', 'read-consistency', 'write-consistency', 'quorum',
            'consensus', 'raft', 'paxos', 'byzantine', 'fault-tolerance', 'byzantine-fault-tolerance',
            'byzantine-general', 'two-phase-commit', '2pc', '3pc', 'saga', 'compensating',
            'transaction', 'acid', 'base', 'cap', 'pacelc', 'brewer', 'consistency',
            'availability', 'partition-tolerance', 'latency', 'throughput', 'bandwidth',
            'jitter', 'packet-loss', 'congestion', 'buffering', 'qos', 'sla', 'slo',
            'error-rate', 'success-rate', 'uptime', 'downtime', 'mtbf', 'mttr',
            'rpo', 'rto', 'backup', 'restore', 'recovery', 'disaster', 'failover',
            'security', 'encryption', 'authentication', 'authorization', 'audit',
            'compliance', 'gdpr', 'hipaa', 'pci-dss', 'soc2', 'iso27001', 'nist',
            'cis', 'owasp', 'sans', 'mitre', 'cve', 'cvss', 'vulnerability',
            'exploit', 'payload', 'shellcode', 'rootkit', 'malware', 'ransomware',
            'trojan', 'virus', 'worm', 'botnet', 'ddos', 'dos', 'syn-flood',
            'firewall', 'ids', 'ips', 'waf', 'vpn', 'proxy', 'reverse-proxy',
            'load-balancer', 'cdn', 'dns', 'dhcp', 'nat', 'pat', 'routing',
            'bgp', 'ospf', 'eigrp', 'isis', 'rip', 'mpls', 'vlan', 'vxlan',
            'geneve', 'nvgre', 'gre', 'ipsec', 'ssl', 'tls', 'dtls', 'quic',
            'http', 'https', 'http2', 'http3', 'spdy', 'smtp', 'pop3', 'imap',
            'ftp', 'sftp', 'scp', 'rsync', 'nfs', 'smb', 'cifs', 'afp',
            'ntp', 'sntp', 'snmp', 'syslog', 'netflow', 'sflow', 'ipfix',
            'ldap', 'kerberos', 'radius', 'tacacs', 'saml', 'oauth', 'oidc',
            'jwt', 'jws', 'jwe', 'pkix', 'x509', 'pem', 'der', 'pkcs',
            'rsa', 'dsa', 'ecdsa', 'eddsa', 'aes', 'des', '3des', 'rc4',
            'md5', 'sha1', 'sha256', 'sha512', 'blake2', 'blake3', 'argon2',
            'bcrypt', 'scrypt', 'pbkdf2', 'hmac', 'cmac', 'gmac', 'poly1305',
            'chacha20', 'salsa20', 'xsalsa20', 'xchacha20', 'curve25519',
            'curve448', 'x25519', 'x448', 'ed25519', 'ed448', 'secp256k1',
            'secp256r1', 'secp384r1', 'secp521r1', 'brainpool', 'sm2', 'sm3',
            'sm4', 'zuc', 'lea', 'aria', 'camellia', 'seed', 'idea', 'blowfish',
            'twofish', 'serpent', 'cast', 'rc2', 'rc5', 'rc6', 'skipjack',
            'mars', 'rijndael', 'loki', 'safer', 'feal', 'misty', 'kasumi',
            'e2', 'khazad', 'anubis', 'hierocrypt', 'square', 'shark', 'ciphertext',
            'plaintext', 'key', 'iv', 'nonce', 'salt', 'pepper', 'hash',
            'digest', 'signature', 'certificate', 'ca', 'crl', 'ocsp', 'timestamp',
            'notary', 'tuf', 'in-toto', 'slsa', 'sbom', 'spdx', 'cyclonedx',
            'provenance', 'attestation', 'evidence', 'audit', 'log', 'trace',
            'metric', 'telemetry', 'observability', 'monitoring', 'alerting',
            'incident', 'response', 'postmortem', 'blameless', 'root-cause',
            'analysis', 'rca', 'fmea', 'fta', 'hazop', 'lopa', 'bow-tie',
            'risk', 'assessment', 'mitigation', 'remediation', 'patch', 'update',
            'upgrade', 'downgrade', 'rollback', 'canary', 'blue-green', 'shadow',
            'a/b-test', 'feature-flag', 'circuit-breaker', 'retry', 'timeout',
            'bulkhead', 'rate-limit', 'throttle', 'queue', 'backpressure',
            'flow-control', 'congestion', 'buffering', 'caching', 'memoization',
            'lazy-loading', 'eager-loading', 'prefetching', 'preloading', 'warming',
            'cold-start', 'warm-start', 'hot-start', 'jit', 'aot', 'tiered',
            'compilation', 'optimization', 'inlining', 'loop-unrolling', 'vectorization',
            'simd', 'gpu', 'tpu', 'asic', 'fpga', 'dsa', 'nic', 'smartnic',
            'dpu', 'ipu', 'cpu', 'soc', 'mcu', 'spu', 'alu', 'fpu',
            'cache', 'tlb', 'btb', 'bpu', 'prefetcher', 'speculator', 'predictor',
            'branch', 'jump', 'call', 'return', 'interrupt', 'exception',
            'trap', 'fault', 'abort', 'halt', 'reset', 'nmi', 'smi',
            'privilege', 'ring', 'mode', 'user', 'kernel', 'hypervisor',
            'supervisor', 'protected', 'real', 'virtual', 'paging', 'segmentation',
            'memory', 'address', 'translation', 'mmu', 'iommu', 'smmu',
            'tlb', 'page-table', 'page-walk', 'page-fault', 'page-replacement',
            'lru', 'lfu', 'arc', 'clock', 'fifo', 'random', 'working-set',
            'resident', 'swap', 'paging', 'thrashing', 'oom', 'killer',
            'memory-leak', 'use-after-free', 'double-free', 'buffer-overflow',
            'stack-overflow', 'heap-overflow', 'integer-overflow', 'underflow',
            'format-string', 'sql-injection', 'xss', 'csrf', 'xxe', 'ssrf',
            'lfi', 'rfi', 'path-traversal', 'directory-traversal', 'symlink',
            'race-condition', 'toctou', 'deadlock', 'livelock', 'starvation',
            'priority-inversion', 'convoy', 'thundering-herd', 'cascading-failure',
            'avalanche', 'cascade', 'chain-reaction', 'domino-effect', 'butterfly-effect',
            'chaos', 'resilience', 'antifragility', 'robustness', 'fault-tolerance',
            'graceful-degradation', 'fail-safe', 'fail-secure', 'fail-open', 'fail-closed',
            'defense-in-depth', 'defense-in-breadth', 'defense-in-height', 'defense-in-width',
            'zero-trust', 'least-privilege', 'separation-of-concerns', 'principle-of-least-surprise',
            'fail-fast', 'fail-slow', 'fail-loud', 'fail-silent', 'fail-gracefully',
            'defensive-programming', 'offensive-programming', 'secure-coding', 'secure-design',
            'threat-modeling', 'attack-tree', 'attack-surface', 'attack-vector',
            'vulnerability-disclosure', 'responsible-disclosure', 'coordinated-disclosure',
            'bug-bounty', 'vulnerability-reward', 'penetration-testing', 'red-team',
            'blue-team', 'purple-team', 'white-team', 'black-team', 'green-team',
            'yellow-team', 'orange-team', 'red-flag', 'yellow-flag', 'green-flag',
            'code-review', 'peer-review', 'security-review', 'threat-review',
            'architecture-review', 'design-review', 'implementation-review', 'testing-review',
            'deployment-review', 'operations-review', 'incident-review', 'postmortem-review',
            'lessons-learned', 'knowledge-base', 'runbook', 'playbook', 'handbook',
            'guide', 'tutorial', 'documentation', 'specification', 'standard',
            'rfc', 'ieee', 'iso', 'iec', 'itu', 'etsi', 'ietf',
            'w3c', 'whatwg', 'ecma', 'tc39', 'unicode', 'iso-639', 'iso-3166',
            'iso-4217', 'iso-8601', 'iso-9000', 'iso-27000', 'iso-31000',
            'iso-50001', 'iso-55000', 'iso-90001', 'iso-14000', 'iso-45000',
            'iso-50001', 'iso-55000', 'iso-90001', 'iso-14000', 'iso-45000',
        ]

        for keyword in technical_keywords:
            if keyword in text.lower():
                terms.append(keyword)

        # Clean up and remove duplicates
        terms = list(set(terms))

        # Filter out very common words
        common_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'from', 'up', 'about', 'into', 'through', 'during', 'before', 'after', 'above', 'below', 'between', 'under', 'again', 'further', 'then', 'once', 'here', 'there', 'when', 'where', 'why', 'how', 'all', 'each', 'every', 'both', 'few', 'more', 'most', 'other', 'some', 'such', 'no', 'nor', 'not', 'only', 'own', 'same', 'so', 'than', 'too', 'very', 'can', 'just', 'should', 'now', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'ought', 'may', 'might', 'must', 'shall', 'should', 'this', 'that', 'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they', 'what', 'which', 'who', 'whom', 'whose'}

        terms = [t for t in terms if t not in common_words and len(t) > 2]

        return terms

    def _validate_metadata(self) -> None:
        """Validate the extracted applicationSubCategory."""
        if not self.metadata:
            if self.REQUIRED:
                self.add_error(f"Required field '{self.CODEMETA_PROPERTY}' is missing")
        elif not isinstance(self.metadata, str):
            self.add_error(f"Field '{self.CODEMETA_PROPERTY}' must be a string")
        elif len(self.metadata) > 500:
            self.add_warning(f"Field '{self.CODEMETA_PROPERTY}' is very long ({len(self.metadata)} characters)")

    def to_codemeta_dict(self) -> dict:
        """Convert to Codemeta format."""
        if self.metadata:
            return {self.CODEMETA_PROPERTY: self.metadata}
        return {}
