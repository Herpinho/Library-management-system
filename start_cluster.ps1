$Signature = @'
[DllImport("user32.dll")]
public static extern bool MoveWindow(IntPtr hWnd, int X, int Y, int nWidth, int nHeight, bool bRepaint);
[DllImport("user32.dll")]
public static extern bool SetForegroundWindow(IntPtr hWnd);
'@
if (-not ([System.Management.Automation.PSTypeName]'Win32Utils.Win32').Type) {
    Add-Type -MemberDefinition $Signature -Name Win32 -Namespace Win32Utils
}

$Commands = @(
    @{ cmd = "minikube service user-service";     pos = @(0, 5, 535, 235) },
    @{ cmd = "minikube service loan-service";     pos = @(0, 250, 535, 235) },
    @{ cmd = "minikube service catalog-service";  pos = @(0, 495, 535, 235) },
    @{ cmd = "minikube service payments-service"; pos = @(0, 740, 535, 235) },
    @{ cmd = "kubectl port-forward --address 0.0.0.0 service/payments-service 5004:5004"; pos = @(1570, 300, 350, 115) },
    @{ cmd = "kubectl port-forward --address 0.0.0.0 service/loan-service 5003:5003";     pos = @(1570, 420, 350, 115) },
    @{ cmd = "kubectl port-forward --address 0.0.0.0 service/catalog-service 5002:5002";  pos = @(1570, 540, 350, 115) },
    @{ cmd = "kubectl port-forward --address 0.0.0.0 service/user-service 5001:5001";     pos = @(1570, 660, 350, 115) },
    @{ cmd = "while(`$true) { clear; kubectl get pods; sleep 5 }";        pos = @(1385, 5, 535, 280) },
    @{ cmd = "while(`$true) { clear; kubectl get deployments; sleep 5 }"; pos = @(1495, 785, 425, 215) }
)

foreach ($item in $Commands) {
    $p = Start-Process "conhost.exe" -ArgumentList "powershell.exe -NoExit -Command `"$($item.cmd)`"" -PassThru
    $x, $y, $w, $h = $item.pos

    $timeout = 0
    while ($p.MainWindowHandle -eq 0 -and $timeout -lt 40) {
        Start-Sleep -Milliseconds 200
        $p.Refresh()
        $timeout++
    }

    if ($p.MainWindowHandle -ne 0) {
        [Win32Utils.Win32]::SetForegroundWindow($p.MainWindowHandle) | Out-Null
        Start-Sleep -Milliseconds 300
        [Win32Utils.Win32]::MoveWindow($p.MainWindowHandle, $x, $y, $w, $h, $true) | Out-Null
    }
}

Write-Host "[SUCCESS] Dashboard layout applied using conhost." -ForegroundColor Green