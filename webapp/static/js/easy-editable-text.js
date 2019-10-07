$(document).ready(function(){

	$('.edit').click(function(){
		// Hide edit icon, show save icon
		$(this).hide();
		$(this).next().children().first().show();

		// Hide text, show and select input field
		$(this).parent().prev().children().first().hide();
		$(this).parent().prev().children().first().next().show();
		$(this).parent().prev().children().first().next().select();
	});
	
	$('.save').mousedown(function(){
		var cid = $(this).attr('id');
		var form = "update_category";
		var form_id = form.concat(cid);
		// Hide save icon, show edit icon
		$(this).hide();
		$(this).parent().prev().show();

		// Hide input field, show text
		$(this).parent().prev().children().first().show();
		$(this).parent().prev().children().first().next().show();

		document.getElementById(form_id).submit();
		$(this).data('clicked', true);
	});
	
	$('.edit_input').blur(function() {
		if(!$(this).parent().next().children().first().next().next().children().first().data('clicked')){
			this.value = (this.defaultValue ? this.defaultValue : '');
		}else{
			var cid = $(this).attr('id');
			var form = "update_category";
			var form_id = form.concat(cid);
			document.getElementById(form_id).submit();
		}
			// Hide input field, show text
		$(this).hide();
		$(this).prev().show();

		// Show edit icon, hide save icon
		$(this).parent().next().children().first().next().show();
		$(this).parent().next().children().first().next().next().children().first().hide();
			
		// }
		// else{
		// 	$(this).prev().html(this.value);
		// 	this.defaultValue=this.value;
		// }
	});

	$('.edit_input').keypress(function(event) {
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

			// Hide input field, show text
			$(this).hide();
			$(this).prev().show();

			// Show edit icon, hide save icon
			$(this).parent().next().children().first().next().show();
			$(this).parent().next().children().first().next().next().children().first().hide();

			document.getElementById("update_category").submit();
		  }
	  });
});
