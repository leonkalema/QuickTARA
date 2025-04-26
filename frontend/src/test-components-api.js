// Simple test script to directly test the components API
const axios = require('axios');

async function testComponentsAPI() {
  try {
    console.log('Testing direct API call to components endpoint...');
    
    // Direct axios call to the components API with the exact parameters from curl
    const response = await axios.get('http://127.0.0.1:8080/api/components?skip=0&limit=100', {
      headers: {
        'accept': 'application/json'
      }
    });
    
    console.log('API Response Status:', response.status);
    console.log('Response headers:', response.headers);
    console.log('Response data type:', typeof response.data);
    
    if (Array.isArray(response.data)) {
      console.log('Response is an array with', response.data.length, 'items');
      if (response.data.length > 0) {
        console.log('First item sample:', JSON.stringify(response.data[0], null, 2));
      }
    } else if (response.data && typeof response.data === 'object') {
      console.log('Response is an object with keys:', Object.keys(response.data));
      if (response.data.components && Array.isArray(response.data.components)) {
        console.log('Found components array with', response.data.components.length, 'items');
      }
    }
    
    return response.data;
  } catch (error) {
    console.error('API Test Error:', error.message);
    if (error.response) {
      console.error('Status:', error.response.status);
      console.error('Data:', error.response.data);
      console.error('Headers:', error.response.headers);
    } else if (error.request) {
      console.error('No response received:', error.request);
    }
    return null;
  }
}

// Run the test
testComponentsAPI()
  .then(data => {
    console.log('Test complete!');
  })
  .catch(err => {
    console.error('Test failed:', err);
  });
