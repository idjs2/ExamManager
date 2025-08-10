<%@ page language="java" contentType="text/html; charset=UTF-8"
	pageEncoding="UTF-8"%>
<%@ taglib uri="http://java.sun.com/jsp/jstl/core" prefix="c" %>	

<div class="container-fluid">

	<!-- Content Row -->
	<div class="row">

		<div class="col-lg-6 mb-4">

			<!-- Illustrations -->
			<div class="card shadow mb-4">
				<div class="card-header py-3">
					<h3 class="m-0 font-weight-bold text-primary text-center">OMR</h3>
				</div>
				<div class="card-body">
					<div class="text-center">
						<form action="" method="post">
							<div>
								<label>
									<input type="radio" name="choice" value="1" /> 옵션 1
								</label>
								<label>
									<input type="radio" name="choice" value="2" /> 옵션 2
								</label>
								<label>
									<input type="radio" name="choice" value="3" /> 옵션 3
								</label>
								<label>
									<input type="radio" name="choice" value="4" /> 옵션 4
								</label>
								<label>
									<input type="radio" name="choice" value="5" /> 옵션 5
								</label>
							</div>
						</form>
					</div>


				</div>
			</div>

		</div>
	</div>

</div>

<script>
	const radios = document.querySelectorAll('input[name="choice"]');
	
	radios.forEach(radio => {
		radio.addEventListener('change', function() {
			console.log("선택 : ", this.value)
		});
	});
</script>