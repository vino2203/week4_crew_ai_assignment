# CloudSync Admin Guide

## Page 1

CloudSync is our enterprise file synchronization platform. This guide covers
installation, account administration, sync conflict resolution, and security
settings for workspace administrators.

To install the CloudSync desktop client, download the installer from the admin
portal under Settings > Downloads. Supported platforms are Windows 10/11, macOS
12+, and major Linux distributions via the .deb or .rpm package.

## Page 2

### Managing Sync Conflicts

When two users edit the same file offline and reconnect, CloudSync creates a
conflict copy named `<filename> (Conflicted Copy - <device> - <date>).<ext>`
rather than silently overwriting either version.

To resolve a sync conflict as an administrator:
1. Open the Admin Console and navigate to Activity > Conflicts.
2. Select the conflicted file to view both versions side-by-side.
3. Choose "Keep Mine", "Keep Theirs", or "Keep Both" to resolve.
4. CloudSync will re-index the folder automatically after resolution.

If conflicts recur repeatedly for the same file, check whether the file is
open in an application that locks it (e.g. Excel) on one of the devices.

## Page 3

### Account Lockouts and Password Resets

If a user is locked out after 5 failed login attempts, the account is frozen
for 30 minutes. Administrators can manually unlock an account immediately via
Admin Console > Users > select user > "Unlock Account".

Password resets can be triggered by the user via "Forgot Password" on the
login screen, or forced by an administrator via Admin Console > Users >
"Force Password Reset", which emails the user a one-time reset link valid for
24 hours.

Two-factor authentication (2FA) is required for all administrator accounts and
optional (but recommended) for standard users. 2FA can be reset by an admin if
a user loses their authenticator device.

## Page 4

### Storage Quotas and Billing

Each workspace has a pooled storage quota shown in Admin Console > Billing >
Storage. When a workspace exceeds 90% of its quota, all users receive an
in-app warning. At 100%, new file uploads are blocked but existing sync
continues to read.

To increase storage, administrators can upgrade the plan tier or purchase
additional storage blocks (500GB increments) from Admin Console > Billing >
Upgrade. Downgrades take effect at the start of the next billing cycle.
