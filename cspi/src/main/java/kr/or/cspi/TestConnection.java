package kr.or.cspi;

import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.SQLException;

public class TestConnection {
    public static void main(String[] args) {
        // 1. Supavisor(Session Pooler) 연결 정보로 수정
        String url = "jdbc:postgresql://aws-0-ap-northeast-2.pooler.supabase.com:5432/postgres?sslmode=require";
        String user = "postgres.vzamkqsjcnyvypefisbc";
        String password = "cspi1234!acroom11!"; // 실제 비밀번호로 변경

        try (Connection conn = DriverManager.getConnection(url, user, password)) {
            System.out.println("✅ 연결 성공!");
        } catch (SQLException e) {
            // 상세한 오류 정보 출력
            System.err.println("❌ SQL 에러 발생:");
            System.err.println("에러 메시지: " + e.getMessage());
            System.err.println("SQL 상태 코드: " + e.getSQLState());
            System.err.println("에러 코드: " + e.getErrorCode());
            System.err.println("스택 트레이스:");
            e.printStackTrace();
            
            // 추가적인 연결 문제 진단 정보
            System.err.println("\n=== 연결 문제 진단 정보 ===");
            System.err.println("JDBC URL: " + url);
            System.err.println("사용자: " + user);
            System.err.println("비밀번호 길이: " + (password != null ? password.length() : "null"));
        } catch (Exception e) {
            System.err.println("❌ 일반 예외 발생:");
            e.printStackTrace();
        }
    }
}
