var fs = require('fs');
  
// Use fs.readFile() method to read the file
fs.readFile('right-teachable.html', 'utf8', function(err, data){
      
    // Display the file content
    console.log(data);
});