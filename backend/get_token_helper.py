#!/usr/bin/env python3
"""
Helper script to get JWT token from browser
Run this and follow the instructions
"""

print("="*70)
print("JWT TOKEN EXTRACTION GUIDE")
print("="*70)
print()
print("Follow these steps to get your JWT token:")
print()
print("1. Open your browser and go to: http://localhost:3000")
print()
print("2. Login with Google OAuth (if not already logged in)")
print()
print("3. Press F12 to open Developer Tools")
print()
print("4. Click on the 'Console' tab")
print()
print("5. Type this command and press Enter:")
print()
print("   localStorage.getItem('token')")
print()
print("6. You'll see output like:")
print('   "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZC..."')
print()
print("7. Copy the ENTIRE token (including quotes)")
print()
print("8. Remove the quotes and paste it below:")
print()
print("="*70)
print()

token = input("Paste your JWT token here: ").strip().strip('"').strip("'")

if not token or token == "":
    print("\n❌ No token provided!")
    exit(1)

if len(token) < 50:
    print(f"\n⚠️  Token seems too short ({len(token)} chars)")
    print("Make sure you copied the complete token!")
    exit(1)

if "…" in token or "..." in token:
    print("\n⚠️  Token appears truncated (contains ellipsis)")
    print("Make sure to copy the FULL token from the console!")
    exit(1)

# Validate token format
parts = token.split(".")
if len(parts) != 3:
    print(f"\n⚠️  Invalid JWT format (expected 3 parts, got {len(parts)})")
    print("JWT tokens should have format: header.payload.signature")
    exit(1)

print(f"\n✅ Token looks valid! ({len(token)} characters)")
print()
print("Now update test_queries_automated.py:")
print()
print("Replace this line:")
print('JWT_TOKEN = "YOUR_JWT_TOKEN_HERE"')
print()
print("With:")
print(f'JWT_TOKEN = "{token}"')
print()
print("="*70)
print()

# Optionally write to file
save = input("Save token to token.txt file? (y/n): ").strip().lower()
if save == 'y':
    with open('token.txt', 'w') as f:
        f.write(token)
    print("✅ Token saved to token.txt")
    print()
    print("You can now run:")
    print("  python3 test_queries_automated.py")
