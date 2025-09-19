import java.io.BufferedReader;
import java.io.InputStreamReader;

public class WifiScanner {
    public static void main(String[] args) {
        System.out.println("Avvio ricerca wifi...\n\n");
        try {
            Process process = Runtime.getRuntime().exec("netsh wlan show networks mode=bssid");
            BufferedReader reader = new BufferedReader(new InputStreamReader(process.getInputStream()));
            String line;
            while((line = reader.readLine()) != null) {
                System.out.println(line);
            }
            process.waitFor();
        } catch (Exception e) {
            System.out.println("Errore nella ricerca delle Wifi!");
        }
    }
}
