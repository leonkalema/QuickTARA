/**
 * Direct Testing Functions for Attack Path API
 * 
 * This file contains functions to test the attack path API directly,
 * bypassing the API client abstraction to diagnose issues.
 */

// Function to test the attack paths endpoint directly
export async function testAttackPathsAPI() {
  try {
    console.log("TEST: Direct API call to attack paths endpoint");
    const url = 'http://127.0.0.1:8080/api/attack-paths?skip=0&limit=100';
    console.log("Testing URL:", url);
    
    const response = await fetch(url, {
      method: 'GET',
      headers: {
        'Accept': 'application/json'
      },
      mode: 'cors',
      credentials: 'omit'
    });
    
    console.log("Response status:", response.status);
    
    if (response.ok) {
      const data = await response.json();
      console.log("Received data:", data);
      
      if (data.paths) {
        console.log("Paths found:", data.paths.length);
        return data.paths;
      } else {
        console.warn("No 'paths' property in response:", data);
        return [];
      }
    } else {
      console.error("Error response:", await response.text());
      return [];
    }
  } catch (error) {
    console.error("Error testing attack paths API:", error);
    return [];
  }
}

// Function to test the attack chains endpoint directly
export async function testAttackChainsAPI() {
  try {
    console.log("TEST: Direct API call to attack chains endpoint");
    const url = 'http://127.0.0.1:8080/api/attack-paths/chains?skip=0&limit=100';
    console.log("Testing URL:", url);
    
    const response = await fetch(url, {
      method: 'GET',
      headers: {
        'Accept': 'application/json'
      },
      mode: 'cors',
      credentials: 'omit'
    });
    
    console.log("Response status:", response.status);
    
    if (response.ok) {
      const data = await response.json();
      console.log("Received data:", data);
      
      if (data.chains) {
        console.log("Chains found:", data.chains.length);
        return data.chains;
      } else {
        console.warn("No 'chains' property in response:", data);
        return [];
      }
    } else {
      console.error("Error response:", await response.text());
      return [];
    }
  } catch (error) {
    console.error("Error testing attack chains API:", error);
    return [];
  }
}
