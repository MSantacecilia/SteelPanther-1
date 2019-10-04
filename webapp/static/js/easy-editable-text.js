$(document).ready(function(){

	$('.edit').click(function(){
		$(this).hide();
		$(this).parent().prev().children().first().hide();
		$(this).parent().prev().children().first().next().next().show();
		$(this).parent().prev().children().first().next().show();
		$(this).parent().prev().children().first().next().select();
	});


	$('input[type="text"]').blur(function() {
         if ($.trim(this.value) == ''){
			 this.value = (this.defaultValue ? this.defaultValue : '');
		 }
		 else{
			 $(this).prev().html(this.value);
			 // TODO send this.value to database
			 this.defaultValue=this.value;
		 }

		 $(this).hide();
		 $(this).next().hide();
		 $(this).prev().show();
		 $(this).parent().next().children().first().next().show();
     });

	  $('input[type="text"]').keypress(function(event) {
		  if (event.keyCode == '13') {
			  if ($.trim(this.value) == ''){
				 this.value = (this.defaultValue ? this.defaultValue : '');
			 }
			 else
			 {
				 $(this).prev().html(this.value);
				 // TODO send this.value to database
				 this.defaultValue=this.value;
			 }

			 $(this).hide();
			 $(this).next().hide();
			 $(this).prev().show();
			 $(this).parent().next().children().first().next().show();
		  }
	  });

});
