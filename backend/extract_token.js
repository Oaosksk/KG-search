// Run this in browser console (F12 → Console) at http://localhost:3000
// After logging in with Google OAuth

console.log("=".repeat(60));
console.log("JWT TOKEN:");
console.log("=".repeat(60));
console.log(localStorage.getItem('token'));
console.log("=".repeat(60));
console.log("\nCopy the token above and paste it into test_queries_automated.py");
console.log("Replace: JWT_TOKEN = \"YOUR_JWT_TOKEN_HERE\"");
console.log("With:    JWT_TOKEN = \"<your_token>\"");
