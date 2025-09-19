public class BubbleSort {
    public static void main(String[] args) {
        // Sistemare array
        int[] array = {20,12,34,21,45,67};

        for (int i = 0; i < array.length; i++) {
            for (int j = 0; j < array.length; j++) {
                if (array[i] < array[j]) {
                    int temp = array[i];
                    array[i] = array[j];
                    array[j] = temp;
                }
            }
        }

        for (int num : array) {
            System.out.println(num);
        }
    }
}
