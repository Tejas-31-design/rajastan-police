$gitExe = "C:\Users\bhada\AppData\Local\MinGit\cmd\git.exe"

# 1. Initialize Git
& $gitExe init

# 2. Configure user
& $gitExe config user.name "Tejas-31-design"
& $gitExe config user.email "Tejas-31-design@users.noreply.github.com"

# 3. Rename branch to main
& $gitExe branch -M main

# 4. Add all files
& $gitExe add .

# 5. Check staged files count
$staged = & $gitExe status --porcelain
Write-Output "STAGED_FILES_COUNT: $($staged.Count)"

# 6. Commit
& $gitExe commit -m "Initial commit: Fraud Shield - Rajasthan Police Hackathon 2026 (PS01)"

# 7. Add remote
& $gitExe remote remove origin 2>$null
& $gitExe remote add origin "https://github.com/Tejas-31-design/rajastan-police.git"

Write-Output "GIT_INIT_AND_COMMIT_COMPLETED"
