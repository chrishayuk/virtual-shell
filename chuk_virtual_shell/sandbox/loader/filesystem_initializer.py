# chuk_virtual_shell/sandbox/loader/filesystem_initializer.py
import os
import traceback
import logging
import re
from typing import Dict, Any

from chuk_virtual_fs import VirtualFileSystem  # type: ignore
from chuk_virtual_fs.template_loader import TemplateLoader  # type: ignore

logger = logging.getLogger(__name__)


def load_dotenv():
    """Load .env file if it exists in the current directory."""
    env_file = os.path.join(os.getcwd(), '.env')
    if os.path.exists(env_file):
        try:
            with open(env_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        key = key.strip()
                        value = value.strip().strip('"').strip("'")
                        os.environ[key] = value
            logger.debug(f"Loaded environment variables from {env_file}")
        except Exception as e:
            logger.warning(f"Error loading .env file: {e}")
    else:
        logger.debug("No .env file found")


def compile_denied_patterns(patterns: list) -> list:
    compiled = []
    for pattern in patterns:
        try:
            compiled.append(re.compile(pattern))
        except re.error as e:
            logger.warning(f"Invalid regex pattern '{pattern}': {e}")
    return compiled


def create_filesystem(config: Dict[str, Any]) -> VirtualFileSystem:
    """
    Create a VirtualFileSystem instance based on the sandbox config.
    """
    logger.debug("Creating filesystem from config")
    
    # Load .env file to get credentials
    load_dotenv()
    
    # Debug: Show what credentials are available
    tigris_creds = [k for k in os.environ.keys() if 'TIGRIS' in k]
    aws_creds = [k for k in os.environ.keys() if k.startswith('AWS_')]
    if tigris_creds:
        logger.debug(f"Found Tigris credentials: {tigris_creds}")
    if aws_creds:
        logger.debug(f"Found AWS credentials: {aws_creds}")

    security_config = config.get("security", {})
    if "denied_patterns" in security_config:
        security_config["denied_patterns"] = compile_denied_patterns(
            security_config["denied_patterns"]
        )

    fs_config = config.get("filesystem", {})
    provider_name = fs_config.get("provider", "memory")
    provider_args = fs_config.get("provider_args", {}).copy()

    # Enhanced provider args with environment variables (same as main.py)
    if provider_name == 's3':
        # Auto-detect S3 credentials from environment if not provided
        if not provider_args.get('bucket_name'):
            if 'S3_BUCKET_NAME' in os.environ:
                provider_args['bucket_name'] = os.environ['S3_BUCKET_NAME']
            elif 'TIGRIS_BUCKET_NAME' in os.environ:
                provider_args['bucket_name'] = os.environ['TIGRIS_BUCKET_NAME']
        
        # Pass credentials explicitly to the provider
        # Check for Tigris-specific credentials first, then fall back to AWS
        if 'TIGRIS_ACCESS_KEY_ID' in os.environ and 'TIGRIS_SECRET_ACCESS_KEY' in os.environ:
            provider_args['aws_access_key_id'] = os.environ['TIGRIS_ACCESS_KEY_ID']
            provider_args['aws_secret_access_key'] = os.environ['TIGRIS_SECRET_ACCESS_KEY']
        elif 'AWS_ACCESS_KEY_ID' in os.environ and 'AWS_SECRET_ACCESS_KEY' in os.environ:
            provider_args['aws_access_key_id'] = os.environ['AWS_ACCESS_KEY_ID']
            provider_args['aws_secret_access_key'] = os.environ['AWS_SECRET_ACCESS_KEY']
                
        # Set endpoint for Tigris if credentials are present
        if any(key in os.environ for key in ['TIGRIS_ACCESS_KEY_ID', 'TIGRIS_SECRET_ACCESS_KEY']):
            if 'endpoint_url' not in provider_args and 'AWS_ENDPOINT_URL_S3' not in os.environ:
                provider_args['endpoint_url'] = 'https://t3.storage.dev'
        
        # Add endpoint URL if specified in environment
        if 'AWS_ENDPOINT_URL_S3' in os.environ:
            provider_args.setdefault('endpoint_url', os.environ['AWS_ENDPOINT_URL_S3'])
        
        # Add region for S3 provider and S3 addressing style for Tigris
        is_tigris = 't3.storage.dev' in provider_args.get('endpoint_url', '').lower() or 'tigris' in provider_args.get('endpoint_url', '').lower()
        
        if is_tigris:
            # Tigris configuration - override region if it's "auto"
            if 'AWS_REGION' in os.environ and os.environ['AWS_REGION'] != 'auto':
                provider_args.setdefault('region_name', os.environ['AWS_REGION'])
            elif 'AWS_DEFAULT_REGION' in os.environ:
                provider_args.setdefault('region_name', os.environ['AWS_DEFAULT_REGION'])
            else:
                provider_args.setdefault('region_name', 'us-east-1')
# provider_args.setdefault('s3_addressing_style', 'virtual')  # Not supported by chuk_virtual_fs
        else:
            # Standard AWS S3
            if 'AWS_REGION' in os.environ:
                provider_args.setdefault('region_name', os.environ['AWS_REGION'])
            elif 'AWS_DEFAULT_REGION' in os.environ:
                provider_args.setdefault('region_name', os.environ['AWS_DEFAULT_REGION'])
    
    logger.debug(f"Using provider args for {provider_name}: {provider_args}")
    
    # Debug: Show final configuration that will be passed
    logger.info(f"Final provider configuration:")
    logger.info(f"  Provider: {provider_name}")
    logger.info(f"  Endpoint: {provider_args.get('endpoint_url', 'default')}")
    logger.info(f"  Bucket: {provider_args.get('bucket_name', 'not specified')}")
    logger.info(f"  Region: {provider_args.get('region_name', 'default')}")
    logger.info(f"  S3 Addressing: {provider_args.get('s3_addressing_style', 'default')}")
    logger.info(f"  Has credentials: {'aws_access_key_id' in provider_args}")
    if 'aws_access_key_id' in provider_args:
        key_id = provider_args['aws_access_key_id']
        logger.info(f"  Access key ID: {key_id[:8]}...{key_id[-4:] if len(key_id) > 12 else '***'}")
    
    # Don't log the full provider_args as it contains credentials

    security_profile = security_config.get("profile")

    logger.debug(f"Creating filesystem with provider {provider_name}")
    try:
        fs = VirtualFileSystem(
            provider_name=provider_name, security_profile=security_profile, **provider_args
        )
    except Exception as e:
        # Enhanced error handling for S3/Tigris issues
        if provider_name == 's3':
            # Check environment variables to provide better guidance
            has_tigris_creds = any(key in os.environ for key in ['TIGRIS_ACCESS_KEY_ID', 'TIGRIS_SECRET_ACCESS_KEY'])
            has_aws_creds = any(key in os.environ for key in ['AWS_ACCESS_KEY_ID', 'AWS_SECRET_ACCESS_KEY'])
            is_tigris = 't3.storage.dev' in provider_args.get('endpoint_url', '').lower() or 'tigris' in provider_args.get('endpoint_url', '').lower()
            
            logger.error(f"S3 provider initialization failed: {str(e)}")
            
            if is_tigris:
                logger.error("This appears to be a Tigris configuration.")
                if not has_tigris_creds and not has_aws_creds:
                    logger.error("No Tigris or AWS credentials found. Please set:")
                    logger.error("  export TIGRIS_ACCESS_KEY_ID=<your_access_key>")
                    logger.error("  export TIGRIS_SECRET_ACCESS_KEY=<your_secret_key>")
                    logger.error("  Get credentials from: https://console.tigris.dev/")
                    logger.error("  Or add them to your .env file")
                elif has_tigris_creds:
                    logger.error("Tigris credentials found but access denied.")
                    logger.error("Please check your credentials and bucket permissions.")
                elif has_aws_creds:
                    logger.error("Using AWS credentials for Tigris - this might work if configured correctly.")
            else:
                logger.error("This appears to be an AWS S3 configuration.")
                if not has_aws_creds:
                    logger.error("No AWS credentials found. Please set:")
                    logger.error("  export AWS_ACCESS_KEY_ID=<your_access_key>")
                    logger.error("  export AWS_SECRET_ACCESS_KEY=<your_secret_key>")
        raise

    # Apply additional security settings
    if (
        security_config
        and hasattr(fs, "provider")
        and hasattr(fs.provider, "_in_setup")
    ):
        fs.provider._in_setup = True
        for key, value in security_config.items():
            if key != "profile" and hasattr(fs.provider, key):
                setattr(fs.provider, key, value)

    # Handle filesystem template if specified
    if "filesystem-template" in config:
        template_config = config["filesystem-template"]
        if "name" not in template_config:
            logger.warning("Filesystem template name not specified in config.")
        else:
            template_name = template_config["name"]
            template_variables = template_config.get("variables", {})
            template_loader = TemplateLoader(fs)
            try:
                template_path = _find_template(template_name)
                if template_path:
                    template_loader.load_template(
                        template_path, variables=template_variables
                    )
                else:
                    logger.warning(f"Filesystem template '{template_name}' not found.")
            except Exception as e:
                logger.error(
                    f"Error applying filesystem template '{template_name}': {e}"
                )
                traceback.print_exc()

    if hasattr(fs, "provider") and hasattr(fs.provider, "_in_setup"):
        fs.provider._in_setup = False

    return fs


def _find_template(name: str) -> str:
    """
    Helper function to search standard directories for a template file.
    """
    search_paths = [
        os.getcwd(),
        os.path.join(os.getcwd(), "templates"),
        os.path.expanduser("~/.chuk_virtual_shell/templates"),
        "/usr/share/virtual-shell/templates",
    ]

    if "CHUK_VIRTUAL_SHELL_TEMPLATE_DIR" in os.environ:
        search_paths.insert(0, os.environ["CHUK_VIRTUAL_SHELL_TEMPLATE_DIR"])

    file_patterns = [
        f"{name}.yaml",
        f"{name}.yml",
        f"{name}_template.yaml",
        f"{name}_template.yml",
        f"{name}.json",
    ]

    for path in search_paths:
        if not os.path.exists(path):
            continue
        for pattern in file_patterns:
            template_path = os.path.join(path, pattern)
            logger.debug(f"Checking for template at {template_path}")
            if os.path.exists(template_path):
                logger.debug(f"Found template at {template_path}")
                return template_path
    return ""
