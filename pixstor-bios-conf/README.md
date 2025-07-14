# PixStor BIOS Configuration Tool

A utility script for standardizing BIOS configurations on Dell servers used in PixStor deployments.

## Overview

The `pixstor-bios-conf` tool provides a simple interface to apply standardized BIOS configurations to Dell servers via the Dell RACADM utility. It supports different node profiles for various PixStor deployment types and includes safety features like dry-run mode.

## Prerequisites

- Dell server with iDRAC
- Dell OpenManage tools installed (specifically `racadm`)
- Root/sudo privileges

## Features

- Automated BIOS configuration for PixStor nodes
- Multiple configuration profiles:
  - NVMe Node (with SR-IOV and SubNumaCluster settings)
  - Standard Node
- Dry-run mode for previewing changes without applying them
- Detailed logging via syslog
- Job monitoring with status updates
- Optional automatic reboot after configuration

## Usage

1. Run the script with root privileges:
   ```
   sudo ./pixstor-bios-conf
   ```

2. Select whether to perform a dry-run (preview only) or actual configuration

3. Choose the appropriate node configuration profile:
   - NVMe Node: Optimized for NVMe storage with SR-IOV enabled
   - Standard Node: Standard PixStor node configuration

4. Review the configuration that will be applied

5. Confirm application of the configuration

6. The script will:
   - Create a temporary XML file with the BIOS configuration
   - Submit the configuration job to the iDRAC
   - Monitor the job until completion
   - Offer to reboot the system when complete

## Configuration Details

### NVMe Node Profile
- SubNumaCluster: Disabled
- BootMode: UEFI
- BootSeqRetry: Disabled
- Boot Order: Network PXE first
- System Profile: Performance Optimized
- SR-IOV: Enabled

### Standard Node Profile
- BootMode: UEFI
- BootSeqRetry: Disabled
- Boot Order: Network PXE first
- System Profile: Performance Optimized

## Logging

All operations are logged to syslog with the tag `Pixstor-BIOS` for auditing and troubleshooting purposes.

## Notes

- BIOS changes require a system reboot to take effect
- The script requires local racadm access to the system's BMC
- Always test in dry-run mode first to verify the intended configuration
