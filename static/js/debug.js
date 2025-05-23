/**
 * Debug script for troubleshooting CSS loading issues
 * This should be included temporarily during development
 */
document.addEventListener('DOMContentLoaded', function() {
    // Create debug container
    const debugContainer = document.createElement('div');
    debugContainer.id = 'css-debug-container';
    debugContainer.style.position = 'fixed';
    debugContainer.style.bottom = '10px';
    debugContainer.style.right = '10px';
    debugContainer.style.background = 'rgba(0,0,0,0.7)';
    debugContainer.style.color = 'white';
    debugContainer.style.padding = '10px';
    debugContainer.style.borderRadius = '5px';
    debugContainer.style.fontFamily = 'monospace';
    debugContainer.style.fontSize = '12px';
    debugContainer.style.zIndex = '9999';
    debugContainer.style.maxWidth = '300px';
    debugContainer.style.maxHeight = '200px';
    debugContainer.style.overflow = 'auto';
    
    // Check stylesheet loading
    const stylesheets = document.querySelectorAll('link[rel="stylesheet"]');
    const styleInfo = document.createElement('div');
    styleInfo.innerHTML = '<strong>Stylesheet Loading:</strong>';
    debugContainer.appendChild(styleInfo);

    // Check each stylesheet
    stylesheets.forEach((sheet, index) => {
        const sheetInfo = document.createElement('div');
        const href = sheet.getAttribute('href');
        const shortHref = href.split('/').pop();
        
        // Create a test to see if styles from this sheet are applied
        const testElement = document.createElement('div');
        testElement.style.display = 'none';
        testElement.classList.add(`css-test-${index}`);
        document.body.appendChild(testElement);
        
        const isLoaded = getComputedStyle(testElement).display !== 'none';
        sheetInfo.innerHTML = `${shortHref}: ${isLoaded ? '✓' : '✗'}`;
        sheetInfo.style.color = isLoaded ? '#4ade80' : '#f87171';
        debugContainer.appendChild(sheetInfo);
        
        // Clean up test element
        document.body.removeChild(testElement);
    });
    
    // Check theme state
    const themeInfo = document.createElement('div');
    const currentTheme = document.documentElement.getAttribute('data-theme') || 'light';
    themeInfo.innerHTML = `<strong>Current Theme:</strong> ${currentTheme}`;
    debugContainer.appendChild(themeInfo);
    
    // Display CSS variables
    const variablesInfo = document.createElement('div');
    variablesInfo.innerHTML = '<strong>CSS Variables:</strong>';
    debugContainer.appendChild(variablesInfo);
    
    const importantVars = [
        '--bg-color',
        '--text-color',
        '--primary-color'
    ];
    
    importantVars.forEach(varName => {
        const varValue = getComputedStyle(document.documentElement).getPropertyValue(varName).trim();
        const varInfo = document.createElement('div');
        varInfo.innerHTML = `${varName}: ${varValue || 'not set'}`;
        varInfo.style.color = varValue ? '#4ade80' : '#f87171';
        debugContainer.appendChild(varInfo);
    });
    
    // Add close button
    const closeButton = document.createElement('button');
    closeButton.innerHTML = 'Close';
    closeButton.style.marginTop = '10px';
    closeButton.style.padding = '3px 8px';
    closeButton.style.background = '#6b7280';
    closeButton.style.border = 'none';
    closeButton.style.borderRadius = '3px';
    closeButton.style.color = 'white';
    closeButton.style.cursor = 'pointer';
    closeButton.onclick = function() {
        document.body.removeChild(debugContainer);
    };
    debugContainer.appendChild(closeButton);
    
    // Add container to body
    document.body.appendChild(debugContainer);
    
    // Log to console as well
    console.log('CSS Debug Info:');
    console.log('- Document theme:', currentTheme);
    console.log('- Stylesheets:', Array.from(stylesheets).map(s => s.getAttribute('href')));
    console.log('- CSS Variables:', importantVars.reduce((acc, varName) => {
        acc[varName] = getComputedStyle(document.documentElement).getPropertyValue(varName).trim();
        return acc;
    }, {}));
});