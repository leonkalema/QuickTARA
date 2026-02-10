"""
CRA Product Category Catalog

Official product categories from CRA Annexes III and IV, with technical
descriptions per Implementing Regulation (EU) 2025/2392.

Classification is based on CORE FUNCTIONALITY of the product, not on a
scoring questionnaire. A manufacturer should look at the core functionality
of its product to determine whether it is important or critical.

Key rules (from EU Commission FAQs v1.2):
- Integrating an important/critical component does NOT make the host
  product important/critical.
- Multi-function products are classified by CORE functionality, not
  ancillary functions.
- Products not matching any listed category = Default.
"""
from dataclasses import dataclass
from typing import List, Optional


@dataclass(frozen=True)
class ProductCategory:
    """One official CRA product category."""
    id: str
    name: str
    classification: str  # "class_i" | "class_ii" | "critical"
    description: str
    examples: str
    annex_ref: str


# ── Important Products — Class I (CRA Annex III, Part I) ──────────

CLASS_I_CATEGORIES: List[ProductCategory] = [
    ProductCategory(
        id="CI-01",
        name="Identity management systems and privileged access management",
        classification="class_i",
        description=(
            "Software and hardware for authentication, access control, "
            "and privileged access management, including biometric readers."
        ),
        examples="IAM platforms, PAM tools, biometric access readers",
        annex_ref="Annex III, Class I, (1)",
    ),
    ProductCategory(
        id="CI-02",
        name="Standalone and embedded browsers",
        classification="class_i",
        description="Web browsers for accessing online content, standalone or embedded.",
        examples="Chrome, Firefox, embedded WebView engines",
        annex_ref="Annex III, Class I, (2)",
    ),
    ProductCategory(
        id="CI-03",
        name="Password managers",
        classification="class_i",
        description="Software that stores, generates, and auto-fills credentials.",
        examples="1Password, KeePass, browser built-in password managers",
        annex_ref="Annex III, Class I, (3)",
    ),
    ProductCategory(
        id="CI-04",
        name="Malware detection software",
        classification="class_i",
        description=(
            "Software that searches for, removes, or quarantines "
            "malicious software."
        ),
        examples="Antivirus, EDR agents, anti-malware tools",
        annex_ref="Annex III, Class I, (4)",
    ),
    ProductCategory(
        id="CI-05",
        name="Virtual private networks (VPN)",
        classification="class_i",
        description="Products providing encrypted tunnels for secure remote access.",
        examples="VPN clients, VPN concentrators, VPN gateway appliances",
        annex_ref="Annex III, Class I, (5)",
    ),
    ProductCategory(
        id="CI-06",
        name="Network management systems",
        classification="class_i",
        description="Systems for monitoring, configuring, and managing network infrastructure.",
        examples="SNMP managers, network orchestrators, SDN controllers",
        annex_ref="Annex III, Class I, (6)",
    ),
    ProductCategory(
        id="CI-07",
        name="Security information and event management (SIEM)",
        classification="class_i",
        description="Systems collecting, correlating, and analyzing security events.",
        examples="Splunk, QRadar, SIEM appliances",
        annex_ref="Annex III, Class I, (7)",
    ),
    ProductCategory(
        id="CI-08",
        name="Boot managers",
        classification="class_i",
        description="Software managing the boot process and boot configuration.",
        examples="GRUB, UEFI boot managers, secure boot loaders",
        annex_ref="Annex III, Class I, (8)",
    ),
    ProductCategory(
        id="CI-09",
        name="Public key infrastructure and digital certificate software",
        classification="class_i",
        description="Software for issuing, managing, and validating digital certificates.",
        examples="Certificate authorities, PKI management platforms",
        annex_ref="Annex III, Class I, (9)",
    ),
    ProductCategory(
        id="CI-10",
        name="Physical and virtual network interfaces",
        classification="class_i",
        description="Hardware or software network interface controllers and adapters.",
        examples="NICs, virtual network adapters, network interface firmware",
        annex_ref="Annex III, Class I, (10)",
    ),
    ProductCategory(
        id="CI-11",
        name="Operating systems",
        classification="class_i",
        description="Software managing hardware resources for end-user devices.",
        examples="Linux, Windows, macOS, Android, embedded RTOS",
        annex_ref="Annex III, Class I, (11)",
    ),
    ProductCategory(
        id="CI-12",
        name="Routers, modems, and switches",
        classification="class_i",
        description="Networking devices for internet connection and packet switching.",
        examples="Home routers, cable modems, managed switches",
        annex_ref="Annex III, Class I, (12)",
    ),
    ProductCategory(
        id="CI-13",
        name="Microprocessors with security-related functionalities",
        classification="class_i",
        description="Microprocessors incorporating security features as core function.",
        examples="Secure microprocessors, crypto-capable CPUs",
        annex_ref="Annex III, Class I, (13)",
    ),
    ProductCategory(
        id="CI-14",
        name="Microcontrollers with security-related functionalities",
        classification="class_i",
        description="Microcontrollers incorporating security features as core function.",
        examples="Secure MCUs, TPM-integrated controllers",
        annex_ref="Annex III, Class I, (14)",
    ),
    ProductCategory(
        id="CI-15",
        name="ASICs and FPGAs with security-related functionalities",
        classification="class_i",
        description=(
            "Application-specific integrated circuits and field-programmable "
            "gate arrays with security-related functionalities."
        ),
        examples="Crypto ASICs, security-focused FPGAs",
        annex_ref="Annex III, Class I, (15)",
    ),
    ProductCategory(
        id="CI-16",
        name="Smart home virtual assistants",
        classification="class_i",
        description="Voice-controlled or AI-driven home assistant devices.",
        examples="Smart speakers with assistant, home automation hubs",
        annex_ref="Annex III, Class I, (16)",
    ),
    ProductCategory(
        id="CI-17",
        name="Smart home products with security functionalities",
        classification="class_i",
        description=(
            "Smart door locks, camera systems, baby monitoring systems, "
            "alarm systems, and sensors with security functionality."
        ),
        examples="Smart locks, IP cameras, smart alarm panels, security sensors",
        annex_ref="Annex III, Class I, (17)",
    ),
    ProductCategory(
        id="CI-18",
        name="Internet-connected toys",
        classification="class_i",
        description="Toys with internet connectivity covered by Directive 2009/48/EC.",
        examples="Connected dolls, interactive robots, app-controlled toys",
        annex_ref="Annex III, Class I, (18)",
    ),
    ProductCategory(
        id="CI-19",
        name="Personal wearable products",
        classification="class_i",
        description="Wearable digital products worn or placed on the human body.",
        examples="Smartwatches, fitness trackers, smart rings",
        annex_ref="Annex III, Class I, (19)",
    ),
]


# ── Important Products — Class II (CRA Annex III, Part II) ────────

CLASS_II_CATEGORIES: List[ProductCategory] = [
    ProductCategory(
        id="CII-01",
        name="Hypervisors and container runtime systems",
        classification="class_ii",
        description=(
            "Virtualization software supporting virtualised execution of "
            "operating systems and similar environments."
        ),
        examples="VMware ESXi, KVM, Docker Engine, containerd",
        annex_ref="Annex III, Class II, (1)",
    ),
    ProductCategory(
        id="CII-02",
        name="Firewalls and intrusion detection/prevention systems",
        classification="class_ii",
        description="Network security devices filtering traffic or detecting intrusions.",
        examples="Enterprise firewalls, IDS/IPS appliances, NGFW",
        annex_ref="Annex III, Class II, (2)",
    ),
    ProductCategory(
        id="CII-03",
        name="Tamper-resistant microprocessors",
        classification="class_ii",
        description="Microprocessors designed to resist physical tampering and attacks.",
        examples="Tamper-resistant CPUs, anti-tamper security processors",
        annex_ref="Annex III, Class II, (3)",
    ),
    ProductCategory(
        id="CII-04",
        name="Tamper-resistant microcontrollers",
        classification="class_ii",
        description="Microcontrollers designed to resist physical tampering and attacks.",
        examples="Secure elements in MCU form, tamper-proof controllers",
        annex_ref="Annex III, Class II, (4)",
    ),
    ProductCategory(
        id="CII-05",
        name="Industrial automation and control systems (IACS) for critical entities",
        classification="class_ii",
        description=(
            "IACS intended for use by essential entities as referred to in "
            "Article 3(1) of NIS 2 Directive (EU) 2022/2555."
        ),
        examples="PLCs, DCS, SCADA for critical infrastructure",
        annex_ref="Annex III, Class II, (5)",
    ),
    ProductCategory(
        id="CII-06",
        name="Industrial IoT devices not covered by other categories",
        classification="class_ii",
        description=(
            "Industrial internet-of-things devices with digital elements "
            "not falling under other listed categories."
        ),
        examples="Industrial sensors, industrial gateways, IIoT platforms",
        annex_ref="Annex III, Class II, (6)",
    ),
]


# ── Critical Products (CRA Annex IV) ─────────────────────────────

CRITICAL_CATEGORIES: List[ProductCategory] = [
    ProductCategory(
        id="CR-01",
        name="Hardware security modules (HSM)",
        classification="critical",
        description=(
            "Dedicated cryptographic hardware for secure key management, "
            "encryption, and digital signing operations."
        ),
        examples="Network HSMs, payment HSMs, cloud HSMs",
        annex_ref="Annex IV, (1)",
    ),
    ProductCategory(
        id="CR-02",
        name="Smartcards and similar devices, including secure elements",
        classification="critical",
        description=(
            "Tamper-resistant chips for secure authentication, key storage, "
            "and cryptographic processing."
        ),
        examples="SIM cards, secure elements, smart card ICs, eSIMs",
        annex_ref="Annex IV, (2)",
    ),
    ProductCategory(
        id="CR-03",
        name="Smart meter gateways",
        classification="critical",
        description=(
            "Gateways within smart metering systems for secure energy "
            "metering data exchange and advanced security purposes."
        ),
        examples="Energy smart meter gateways, utility metering hubs",
        annex_ref="Annex IV, (3)",
    ),
]


# ── Combined catalog ──────────────────────────────────────────────

ALL_CATEGORIES: List[ProductCategory] = (
    CLASS_I_CATEGORIES + CLASS_II_CATEGORIES + CRITICAL_CATEGORIES
)

CATEGORY_BY_ID = {cat.id: cat for cat in ALL_CATEGORIES}


def get_all_categories() -> List[ProductCategory]:
    """Return all product categories for UI selection."""
    return ALL_CATEGORIES


def get_category_by_id(category_id: str) -> Optional[ProductCategory]:
    """Look up a single category by its ID."""
    return CATEGORY_BY_ID.get(category_id)
