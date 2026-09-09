"""Permissioned share links with expiry — section 12.

TODO: implement. Design notes:
  - a share link is a signed token carrying report_id + expiry + allowed_roles
  - links must be revocable, so store issued tokens rather than relying on the signature alone
  - every access is an audit event
"""
