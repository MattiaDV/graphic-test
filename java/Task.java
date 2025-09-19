package java;
import java.util.ArrayList;
import java.util.Scanner;

public class Task {
    // Segno le variabili generali
    ArrayList<String> tasks = new ArrayList<>();
    Scanner scanner = new Scanner(System.in);

    // Funzione iniziale
    public void Start() {
        while (true) {
            System.out.println("--- MENU ---\n1) Aggiungere task \n2) Eliminare Task\n3) Modificare Task\n4) Visualizza task\n5) Esci\n------------");
            int choice = scanner.nextInt();
            scanner.nextLine();

            if (choice == 1) {
                System.out.println("Scrivere la task: ");
                String newTask = scanner.nextLine();
                tasks.add(newTask);
                System.out.println("\nTask aggiunto correttamente!\n\n");
            } else if (choice == 2) {
                for (int i = 0; i < tasks.size(); i++) {
                    System.out.println(i + ") " + tasks.get(i));
                }
                int el = scanner.nextInt();
                if (el < 0 || el >= tasks.size()) {
                    System.out.println("\n\nINSERIRE VALORE VALIDO \n\n");
                } else {
                    System.out.println("\nTask " + tasks.get(el) + " eliminato correttamente!\n\n");
                    tasks.remove(el);
                }
            } else if (choice == 3) {
                for (int i = 0; i < tasks.size(); i++) {
                    System.out.println(i + ") " + tasks.get(i));
                }
                int el = scanner.nextInt();
                scanner.nextLine();
                if (el < 0 || el >= tasks.size()) {
                    System.out.println("\n\nINSERIRE VALORE VALIDO \n\n");
                } else {
                    System.out.println("Inserire il task modificato: ");
                    String newTask = scanner.nextLine();
                    System.out.println("\nTask " + tasks.get(el) + " modificato in " + newTask + " correttamente!\n\n");
                    tasks.set(el, newTask);
                }
            } else if (choice == 4) {
                System.out.println("\n--- TASK ---");
                for (int i = 0; i < tasks.size(); i++) {
                    System.out.println(i + ") " + tasks.get(i));
                }
                System.out.println("------------\n\n");
            } else if (choice == 5) {
                System.out.println("\n\nGrazie per aver utilizzato Task, creata da Mattia De Vincentis :)\n\n");
                break;
            }
        }
    }

    public static void main(String[] args) {
        Task app = new Task();
        app.Start();
    }
}
