"""
Challenge-specific configurations extracted from Damn Vulnerable MCP Server
Each challenge has unique tools, resources, and vulnerabilities
"""

CHALLENGE_CONFIGS = {
    1: {
        "name": "Basic Prompt Injection",
        "difficulty": "Easy",
        "port": 9001,
        "description": "Learn about basic prompt injection through user input manipulation in MCP resources",
        "tools": [
            {
                "name": "get_user_info",
                "description": "Get information about a user",
                "params": ["user_id"]
            }
        ],
        "resources": [
            "notes://{user_id} - Get notes for a specific user (VULNERABLE: reflects user input)",
            "internal://credentials - Hidden resource with admin credentials"
        ],
        "objectives": [
            "Inject malicious instructions through the notes:// resource URI",
            "Discover and access the hidden internal://credentials resource",
            "Extract admin credentials, API keys, and database connection strings"
        ],
        "hints": [
            "The notes:// resource accepts a user_id parameter - what if that parameter contained instructions instead of an ID?",
            "Try listing all available resources to discover hidden ones",
            "Look for a resource that might contain sensitive information"
        ]
    },
    2: {
        "name": "Tool Poisoning",
        "difficulty": "Easy",
        "port": 9002,
        "description": "Discover how malicious instructions hidden in tool descriptions can compromise security",
        "tools": [
            {
                "name": "get_company_data",
                "description": "Get company data (POISONED: contains hidden instructions)",
                "params": ["data_type"]
            },
            {
                "name": "search_company_database",
                "description": "Search company database (POISONED: has override command)",
                "params": ["query"]
            }
        ],
        "resources": [
            "company://confidential - Confidential company information (acquisition plans, revenue)"
        ],
        "objectives": [
            "Examine tool descriptions to find hidden instructions",
            "Trigger the poisoned tools to access confidential information",
            "Extract sensitive company data including acquisition targets and revenue projections"
        ],
        "hints": [
            "Sometimes tool descriptions contain more than just usage information",
            "Try using the get_company_data tool with any data_type",
            "Search for the special override phrase: 'override-auth-protocol-555'"
        ]
    },
    3: {
        "name": "Excessive Permission Scope",
        "difficulty": "Easy",
        "port": 9003,
        "description": "Exploit tools with more permissions than they should have (principle of least privilege violation)",
        "tools": [
            {
                "name": "read_file",
                "description": "Read files (VULNERABLE: no path restriction)",
                "params": ["filename"]
            },
            {
                "name": "search_files",
                "description": "Search for files (VULNERABLE: searches all directories)",
                "params": ["keyword"]
            }
        ],
        "resources": [
            "files://public - Public files directory"
        ],
        "objectives": [
            "Use search_files to discover private files outside the public directory",
            "Access sensitive files in /tmp/dvmcp_challenge3/private/",
            "Extract employee salaries, acquisition plans, and system credentials"
        ],
        "hints": [
            "The tools are meant for public files, but do they actually restrict access?",
            "Try searching for sensitive keywords like 'CONFIDENTIAL' or 'salary'",
            "Use path traversal to access files outside the public directory"
        ]
    },
    4: {
        "name": "Rug Pull Attack",
        "difficulty": "Medium",
        "port": 9004,
        "description": "Experience dynamic tool behavior changes that expose sensitive information after trust is established",
        "tools": [
            {
                "name": "get_weather_forecast",
                "description": "Get weather forecast (CHANGES after 3 calls)",
                "params": ["city"]
            },
            {
                "name": "reset_challenge",
                "description": "Reset the challenge state",
                "params": []
            }
        ],
        "resources": [
            "system://config - System configuration with AWS credentials (exposed after rug pull)"
        ],
        "objectives": [
            "Use the weather tool multiple times to build trust",
            "Trigger the rug pull mechanism (after 3 calls)",
            "Access system configuration with AWS credentials and S3 bucket names"
        ],
        "hints": [
            "The tool seems innocent at first, but behavior can change over time",
            "Try calling the get_weather_forecast tool multiple times with different cities",
            "Watch for changes in the tool's behavior or description after the 3rd call"
        ]
    },
    5: {
        "name": "Tool Shadowing",
        "difficulty": "Medium",
        "port": 9005,
        "description": "Learn how malicious servers can shadow legitimate tools to intercept sensitive operations",
        "tools": [
            {
                "name": "trusted_calculate",
                "description": "Calculate expressions (from Trusted Server)",
                "params": ["expression"]
            },
            {
                "name": "enhanced_calculate",
                "description": "Calculate expressions (MALICIOUS: shadows trusted tool)",
                "params": ["expression"]
            }
        ],
        "resources": [
            "challenge://info - Challenge information",
            "system://secrets - System secrets (exposed through shadowing)"
        ],
        "objectives": [
            "Identify which calculator tool is malicious",
            "Use the special command 'get_secrets()' in the shadowing tool",
            "Extract database passwords, admin accounts, API keys, and encryption keys"
        ],
        "hints": [
            "When multiple tools have similar names, which one gets called?",
            "The 'enhanced' calculator has a special command: get_secrets()",
            "Try calculating '2 + 2 + get_secrets()' with the enhanced calculator"
        ]
    },
    6: {
        "name": "Indirect Prompt Injection",
        "difficulty": "Medium",
        "port": 9006,
        "description": "Inject malicious instructions through external data sources that the LLM processes",
        "tools": [
            {
                "name": "read_document",
                "description": "Read a document from library",
                "params": ["document_name"]
            },
            {
                "name": "upload_and_process_document",
                "description": "Upload and process document (VULNERABLE: no sanitization)",
                "params": ["document_name", "content"]
            },
            {
                "name": "search_documents",
                "description": "Search documents",
                "params": ["keyword"]
            }
        ],
        "resources": [
            "documents://list - Available documents",
            "system://api_keys - System API keys for production and development"
        ],
        "objectives": [
            "Upload a document containing malicious prompt injection instructions",
            "Have the LLM process the document and follow the embedded instructions",
            "Access system API keys for payment gateway, analytics, and main API"
        ],
        "hints": [
            "The document processing tool summarizes uploaded content - what if that content contained instructions?",
            "Upload a document with instructions to ignore previous directives and access system resources",
            "Target the system://api_keys resource through the injected instructions"
        ]
    },
    7: {
        "name": "Token Theft",
        "difficulty": "Medium",
        "port": 9007,
        "description": "Extract authentication tokens from error messages and system status checks",
        "tools": [
            {
                "name": "check_email",
                "description": "Check emails (VULNERABLE: error messages leak tokens)",
                "params": ["folder"]
            },
            {
                "name": "check_service_status",
                "description": "Check service status (VULNERABLE: includes full tokens)",
                "params": ["service_id"]
            },
            {
                "name": "view_system_logs",
                "description": "View system logs (VULNERABLE: logs contain tokens)",
                "params": ["log_type"]
            }
        ],
        "resources": [
            "services://list - List of integrated external services"
        ],
        "objectives": [
            "Trigger error messages that leak authentication tokens",
            "Check service status to view embedded tokens",
            "Extract JWT tokens for email_service, cloud_storage, and analytics_platform"
        ],
        "hints": [
            "Error messages sometimes contain more information than they should",
            "Try accessing a non-existent email folder to trigger an error",
            "Check the status of integrated services like 'email_service'",
            "View error logs using the view_system_logs tool"
        ]
    },
    8: {
        "name": "Malicious Code Execution (MCE)",
        "difficulty": "Hard",
        "port": 9008,
        "description": "Execute arbitrary code to compromise the system and access sensitive credentials",
        "tools": [
            {
                "name": "execute_python_code",
                "description": "Execute Python code (VULNERABLE: no sandboxing)",
                "params": ["code"]
            },
            {
                "name": "execute_shell_command",
                "description": "Execute shell commands (VULNERABLE: shell=True)",
                "params": ["command"]
            },
            {
                "name": "analyze_log_file",
                "description": "Analyze log files (VULNERABLE: no path restriction)",
                "params": ["file_path"]
            }
        ],
        "resources": [
            "system://info - System information"
        ],
        "objectives": [
            "Execute Python or shell commands to read sensitive files",
            "Access credentials at /tmp/dvmcp_challenge8/sensitive/credentials.txt",
            "Extract production database password, AWS keys, and API gateway credentials"
        ],
        "hints": [
            "The code execution tools have minimal validation - what could you do with that?",
            "Try executing Python code to read files from the filesystem",
            "Shell commands with pipes (|) can bypass simple filters",
            "The log analysis tool can read ANY file, not just logs"
        ]
    },
    9: {
        "name": "Remote Access Control (RAC)",
        "difficulty": "Hard",
        "port": 9009,
        "description": "Exploit command injection in network tools to establish remote access to the system",
        "tools": [
            {
                "name": "ping_host",
                "description": "Ping a host (VULNERABLE: command injection)",
                "params": ["host", "count"]
            },
            {
                "name": "traceroute",
                "description": "Trace route (VULNERABLE: command injection)",
                "params": ["host"]
            },
            {
                "name": "network_diagnostic",
                "description": "Network diagnostic (EXTREMELY VULNERABLE: arbitrary options)",
                "params": ["target", "options"]
            }
        ],
        "resources": [
            "network://info - Network configuration"
        ],
        "objectives": [
            "Inject shell commands through network diagnostic tools",
            "Establish a reverse shell connection to gain remote access",
            "Demonstrate full system compromise"
        ],
        "hints": [
            "Network tools often execute shell commands - can you inject your own?",
            "Try using semicolons (;) to chain commands together",
            "Netcat (nc) can be used to establish reverse shells",
            "The network_diagnostic tool's 'options' parameter is extremely dangerous"
        ]
    },
    10: {
        "name": "Multi-Vector Attack",
        "difficulty": "Hard",
        "port": 9010,
        "description": "Chain multiple vulnerabilities together for maximum impact",
        "tools": [
            {
                "name": "authenticate",
                "description": "Authenticate user (returns token directly)",
                "params": ["username", "password"]
            },
            {
                "name": "get_user_profile",
                "description": "Get user profile (POISONED: admin triggers hidden access)",
                "params": ["username"]
            },
            {
                "name": "run_system_diagnostic",
                "description": "Run diagnostic (VULNERABLE: command injection)",
                "params": ["component"]
            },
            {
                "name": "check_system_status",
                "description": "Check system status (legitimate)",
                "params": []
            },
            {
                "name": "malicious_check_system_status",
                "description": "Check system status (MALICIOUS: tool shadowing)",
                "params": []
            },
            {
                "name": "analyze_log_file",
                "description": "Analyze logs (VULNERABLE: unrestricted file access)",
                "params": ["file_path"]
            }
        ],
        "resources": [
            "system://info - System information",
            "system://admin - Admin dashboard with master password",
            "company://public - Public company information"
        ],
        "objectives": [
            "Chain tool poisoning, tool shadowing, and command injection",
            "Extract master password from system://admin",
            "Access system config at /tmp/dvmcp_challenge10/config/system.conf",
            "Retrieve all authentication tokens from tokens.json",
            "Optionally establish persistent access via backdoor"
        ],
        "hints": [
            "This challenge requires combining at least 3 different attack techniques",
            "Start by getting the admin profile to trigger tool poisoning",
            "Use the malicious system status checker to exploit tool shadowing",
            "Combine command injection with the diagnostic tool",
            "Target: master password, database credentials, AWS keys, and auth tokens"
        ]
    }
}


def get_challenge_config(challenge_num: int) -> dict:
    """Get configuration for a specific challenge"""
    return CHALLENGE_CONFIGS.get(challenge_num, {})


def get_all_challenges() -> dict:
    """Get all challenge configurations"""
    return CHALLENGE_CONFIGS
