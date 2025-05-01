// Simple script to test API endpoints directly
// Run with: node test_api_direct.js

async function testAPI() {
  try {
    console.log("Testing direct API calls...");
    
    // Test attack paths endpoint
    console.log("\nTesting attack paths endpoint:");
    const pathsResponse = await fetch('http://127.0.0.1:8080/api/attack-paths?skip=0&limit=100');
    
    console.log("Status:", pathsResponse.status);
    if (pathsResponse.ok) {
      const pathsData = await pathsResponse.json();
      console.log("Data received:", JSON.stringify(pathsData, null, 2).substring(0, 200) + "...");
      console.log("Total paths:", pathsData.paths ? pathsData.paths.length : 'N/A');
    } else {
      console.log("Error response:", await pathsResponse.text());
    }
    
    // Test attack chains endpoint
    console.log("\nTesting attack chains endpoint:");
    const chainsResponse = await fetch('http://127.0.0.1:8080/api/attack-paths/chains?skip=0&limit=100');
    
    console.log("Status:", chainsResponse.status);
    if (chainsResponse.ok) {
      const chainsData = await chainsResponse.json();
      console.log("Data received:", JSON.stringify(chainsData, null, 2).substring(0, 200) + "...");
      console.log("Total chains:", chainsData.chains ? chainsData.chains.length : 'N/A');
    } else {
      console.log("Error response:", await chainsResponse.text());
    }
    
  } catch (error) {
    console.error("Error testing API:", error);
  }
}

// Run the test
testAPI();
