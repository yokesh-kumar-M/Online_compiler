export const LANGUAGE_CONFIG = {
  python: {
    name: 'Python 3.12',
    monaco: 'python',
    icon: '🐍',
    color: '#3776AB',
    template: `# Python - Hello World
print("Hello, World! 🌍")

# Variables and data types
name = "CodeForge"
version = 2.0
features = ["Multi-language", "Real-time", "Cloud-based"]

print(f"\\nWelcome to {name} v{version}")
print("\\nFeatures:")
for i, feat in enumerate(features, 1):
    print(f"  {i}. {feat}")

# List comprehension
squares = [x**2 for x in range(1, 6)]
print(f"\\nSquares: {squares}")
`,
  },
  javascript: {
    name: 'JavaScript (Node)',
    monaco: 'javascript',
    icon: '⚡',
    color: '#F7DF1E',
    template: `// JavaScript - Hello World
console.log("Hello, World! 🌍");

// Variables and data types
const name = "CodeForge";
const version = 2.0;
const features = ["Multi-language", "Real-time", "Cloud-based"];

console.log(\`\\nWelcome to \${name} v\${version}\`);
console.log("\\nFeatures:");
features.forEach((feat, i) => {
    console.log(\`  \${i + 1}. \${feat}\`);
});

// Array methods
const squares = Array.from({length: 5}, (_, i) => (i+1) ** 2);
console.log(\`\\nSquares: [\${squares.join(", ")}]\`);
`,
  },
  c: {
    name: 'C (GCC)',
    monaco: 'c',
    icon: '⚙️',
    color: '#A8B9CC',
    template: `#include <stdio.h>

int main() {
    printf("Hello, World! 🌍\\n");
    
    char *name = "CodeForge";
    float version = 2.0;
    
    printf("\\nWelcome to %s v%.1f\\n", name, version);
    
    printf("\\nSquares:\\n");
    for (int i = 1; i <= 5; i++) {
        printf("  %d^2 = %d\\n", i, i * i);
    }
    
    return 0;
}
`,
  },
  cpp: {
    name: 'C++ 17',
    monaco: 'cpp',
    icon: '🔷',
    color: '#00599C',
    template: `#include <iostream>
#include <vector>
#include <string>
using namespace std;

int main() {
    cout << "Hello, World! 🌍" << endl;
    
    string name = "CodeForge";
    double version = 2.0;
    vector<string> features = {"Multi-language", "Real-time", "Cloud-based"};
    
    cout << "\\nWelcome to " << name << " v" << version << endl;
    cout << "\\nFeatures:" << endl;
    for (int i = 0; i < features.size(); i++) {
        cout << "  " << i+1 << ". " << features[i] << endl;
    }
    
    cout << "\\nSquares:" << endl;
    for (int i = 1; i <= 5; i++) {
        cout << "  " << i << "^2 = " << i*i << endl;
    }
    
    return 0;
}
`,
  },
  java: {
    name: 'Java 21',
    monaco: 'java',
    icon: '☕',
    color: '#ED8B00',
    template: `public class Main {
    public static void main(String[] args) {
        System.out.println("Hello, World! 🌍");
        
        String name = "CodeForge";
        double version = 2.0;
        String[] features = {"Multi-language", "Real-time", "Cloud-based"};
        
        System.out.printf("\\nWelcome to %s v%.1f\\n", name, version);
        System.out.println("\\nFeatures:");
        for (int i = 0; i < features.length; i++) {
            System.out.printf("  %d. %s\\n", i+1, features[i]);
        }
        
        System.out.println("\\nSquares:");
        for (int i = 1; i <= 5; i++) {
            System.out.printf("  %d^2 = %d\\n", i, i*i);
        }
    }
}
`,
  },
  go: {
    name: 'Go 1.22',
    monaco: 'go',
    icon: '🔵',
    color: '#00ADD8',
    template: `package main

import "fmt"

func main() {
    fmt.Println("Hello, World! 🌍")
    
    name := "CodeForge"
    version := 2.0
    features := []string{"Multi-language", "Real-time", "Cloud-based"}
    
    fmt.Printf("\\nWelcome to %s v%.1f\\n", name, version)
    fmt.Println("\\nFeatures:")
    for i, feat := range features {
        fmt.Printf("  %d. %s\\n", i+1, feat)
    }
    
    fmt.Println("\\nSquares:")
    for i := 1; i <= 5; i++ {
        fmt.Printf("  %d^2 = %d\\n", i, i*i)
    }
}
`,
  },
};

export const KEYBOARD_SHORTCUTS = [
  { keys: 'Ctrl+Enter', action: 'Run Code' },
  { keys: 'Ctrl+S', action: 'Save Snippet' },
  { keys: 'Ctrl+Shift+F', action: 'Format Code' },
  { keys: 'F5', action: 'Run Code' },
  { keys: 'Ctrl+/', action: 'Toggle Comment' },
  { keys: 'Ctrl+Z', action: 'Undo' },
  { keys: 'Ctrl+Shift+Z', action: 'Redo' },
  { keys: 'Ctrl+D', action: 'Select Word' },
];
