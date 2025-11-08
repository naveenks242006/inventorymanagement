cd <path-to-inventory-management>
ni pom.xml -Value '<paste pom content here>'    # (PowerShell 'ni' = New-Item; easier to paste in editor)
ni .gitignore -Value "target/`n*.log`n*.db`n.vscode/`n*.class"
ni README.md -Value "# Inventory Management (Java, SQLite)`n`nSimple inventory module..."
code .
