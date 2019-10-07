$(document).ready(function(){

	$('.add').click(function(){
		document.getElementById("add_category").submit();
	});

	$('.edit').click(function(){
		var textField = $(this).parent().prev().children().first();

		// Hide edit icon, show save icon
		$(this).hide();
		$(this).next().show();

		// Hide text, show and select input field
		textField.hide();
		textField.next().show();
		textField.next().select();
	});
	
	$('.save').mousedown(function(){
		var cid = $(this).attr('id');
		var form = "update_category"
		var form_id = form.concat(cid);
		
		var textField = $(this).parent().prev().children().first();

		// Hide save icon, show edit icon
		$(this).hide();
		$(this).prev().show();

		// Show text, hide input field
		textField.show();
		textField.next().hide();

		document.getElementById(form_id).submit();
		$(this).data('clicked', true);
	});
	
	$('.edit_input').blur(function() {
		var editIcon = $(this).parent().next().children().first().next();

		if(!editIcon.next().data('clicked')){
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
		editIcon.show();
		editIcon.next().hide();
			
		// }
		// else{
		// 	$(this).prev().html(this.value);
		// 	this.defaultValue=this.value;
		// }
	});

	$('.edit_input').keypress(function(event) {
		if (event.keyCode == '13') {
			var editIcon = $(this).parent().next().children().first().next();

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
			editIcon.show();
			editIcon.next().hide();

			document.getElementById("update_category").submit();
		  }
	  });
});
