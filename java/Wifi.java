import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.io.OutputStreamWriter;
import java.io.PrintWriter;
import java.net.InetSocketAddress;
import java.net.Socket;
import java.nio.charset.StandardCharsets;

public class Wifi {
    public static void main(String[] args) {
        String ip_to_connect = "192.168.1.1";
        int port = 80;

        // opzionale: override da argomenti riga di comando: java Wifi 192.168.1.2 8080
        if (args.length >= 1) ip_to_connect = args[0];
        if (args.length >= 2) {
            try { port = Integer.parseInt(args[1]); } catch (NumberFormatException ignored) {}
        }

        try (Socket socket = new Socket()) {
            // timeout 5s per connessione
            socket.connect(new InetSocketAddress(ip_to_connect, port), 5000);
            System.out.println("Connesso a " + ip_to_connect + ":" + port);

            // Se vuoi inviare una semplice richiesta HTTP GET (se il target è un server web)
            PrintWriter out = new PrintWriter(new OutputStreamWriter(socket.getOutputStream(), StandardCharsets.UTF_8), true);
            BufferedReader in = new BufferedReader(new InputStreamReader(socket.getInputStream(), StandardCharsets.UTF_8));

            // Richiesta HTTP minimale
            out.print("GET / HTTP/1.1\r\n");
            out.print("Host: " + ip_to_connect + "\r\n");
            out.print("Connection: close\r\n");
            out.print("\r\n");
            out.flush();

            // Leggiamo e stampiamo la risposta
            String line;
            while ((line = in.readLine()) != null) {
                System.out.println(line);
            }

            System.out.println("Connessione chiusa.");
        } catch (Exception e) {
            System.err.println("Impossibile connettersi: " + e.getMessage());
            e.printStackTrace();
        }
    }
}
