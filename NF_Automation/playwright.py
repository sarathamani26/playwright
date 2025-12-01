import os
import django
import sys
from NF_Automation.service.NF_ECF_service import NFECF
# from service.NF_ECF_service import NFECF

# Setup Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "your_project.settings")
django.setup()

if __name__ == "__main__":
    # Read args from CLI if needed
    testcasecode = sys.argv[1] if len(sys.argv) > 1 else "AUTECFDONF009 "
    client = sys.argv[2] if len(sys.argv) > 2 else "NF"

    automation = NFECF
    automation.nf_vendor_creationtre22(testcasecode, client)