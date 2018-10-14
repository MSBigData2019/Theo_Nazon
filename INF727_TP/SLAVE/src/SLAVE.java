public class SLAVE {
    public static void main(String[] args) throws InterruptedException {
        Thread.sleep(1000);
        int result = 3 + 2;
        System.out.println("Computing calculation - timeout 3s");
        System.out.println(result);
    }
}
