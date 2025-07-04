package kr.or.cspi;

import java.text.DateFormat;
import java.util.Date;
import java.util.Locale;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestMethod;

/**
 * Handles requests for the application home page.
 */
@Controller
public class HomeController {

	@RequestMapping(value = "/")
	public String home() {
	
		
		return "home";
	}
	
	@RequestMapping(value = "/test")
	public String test1() {
		
		
		return "test/main";
	}
	
	@RequestMapping(value = "/test/board.do")
	public String test2() {
		
		
		return "test/board/board";
	}
	
	@RequestMapping(value = "/home.do")
	public String test3() {
		return "test/home";
	}
	
}
