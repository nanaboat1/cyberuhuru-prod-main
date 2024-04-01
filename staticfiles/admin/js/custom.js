$(document).ready(function(){
	$(".form-row.field-challenge_video").css({'display':'none'});
	$("#id_challenge_cat").blur(function(){
		var challenge_name = $("#id_challenge_cat").val();
		var challengesname = $.trim(challenge_name).toLowerCase();
		var challengesnametext = challengesname.replace(/[^a-z0-9\s]/gi, '').replace(/[_\s]/g, '-');
		$("#challengecategory_form").find("#id_url_alias").val(challengesnametext);
	})
	
	$("#id_goal_name").blur(function(){
		var goals_name = $("#id_goal_name").val();
		var goalsname = $.trim(goals_name).toLowerCase();
		var goalsnametext = goalsname.replace(/[^a-z0-9\s]/gi, '').replace(/[_\s]/g, '-');
		$("#goals_form").find("#id_url_alias").val(goalsnametext);
	})
	
	$("#id_challenge_name").blur(function(){
		var challenge_name = $("#id_challenge_name").val();
		var challengename = $.trim(challenge_name).toLowerCase();
		var challengetext = challengename.replace(/[^a-z0-9\s]/gi, '').replace(/[_\s]/g, '-');
		$("#challenge_form").find("#id_url_alias").val(challengetext);
	})
	$("#id_vtype").change(function(){
		var uploadtype = $(this).children("option:selected").val();
		if(uploadtype == 1){
			$(".form-row.field-challenge_image").show('500');
			$(".form-row.field-challenge_video").hide('500');
		}else if(uploadtype == 2){
			$(".form-row.field-challenge_image").hide('500');
			$(".form-row.field-challenge_video").show('500');
		}else{
			$(".form-row.field-challenge_image").show();
			$(".form-row.field-challenge_video").hide();
		}
	});
	
	challengetype = $("#challenge_form").find("#id_vtype option:selected").val();
	subchallengetype = $("#subchallenge_form").find("#id_subtype option:selected").val();
	if(challengetype == 1){
		$(".form-row.field-challenge_image").show('500');
		$(".form-row.field-challenge_video").hide('500');
	}else if(challengetype == 2){
		$(".form-row.field-challenge_image").hide('500');
		$(".form-row.field-challenge_video").show('500');
	}else{
		$(".form-row.field-challenge_image").show();
		$(".form-row.field-challenge_video").hide();
	}
	
	if(subchallengetype == 1){
		$(".form-row.field-sub_images").show('500');
		$(".form-row.field-sub_video").hide('500');
	}else if(subchallengetype == 2){
		$(".form-row.field-sub_images").hide('500');
		$(".form-row.field-sub_video").show('500');
	}else{
		$(".form-row.field-sub_images").show();
		$(".form-row.field-sub_video").hide();
	}
	
	$("#id_subtype").change(function(){
		var uploadtype = $(this).children("option:selected").val();
		if(uploadtype == 1){
			$(".form-row.field-sub_images").show('500');
			$(".form-row.field-sub_video").hide('500');
		}else if(uploadtype == 2){
			$(".form-row.field-sub_images").hide('500');
			$(".form-row.field-sub_video").show('500');
		}else{
			$(".form-row.field-sub_images").show();
			$(".form-row.field-sub_video").hide();
		}
	});
	
	$("#id_title").blur(function(){
		var sub_title = $("#id_title").val();
		var subchalgtitle = $.trim(sub_title).toLowerCase();
		var subchalgtitletext = subchalgtitle.replace(/[^a-z0-9\s]/gi, '').replace(/[_\s]/g, '-');
		$("#subchallenge_form").find("#id_url_alias").val(subchalgtitletext);
	})

	$('#id_start_date').blur(function(){
	    var startdate = $(this).val();
	    var idday = $("#id_day option:selected").text();
	    var dayid = parseInt(0);
	    if(idday !=null && idday!=undefined){
	    	dayid = parseInt(idday)
	    }
	    var newdate = new Date(startdate);
	    newdate.setDate(newdate.getDate() + dayid);
	    
	    var day = ("0" + newdate.getDate()).slice(-2);
		var month = ("0" + (newdate.getMonth() + 1)).slice(-2);
		var year = newdate.getFullYear();
		var today = year+"-"+month+"-"+day;
		if(today !="NaN-aN-aN"){
			$("#id_end_date").val(today);
		}else{
			$("#id_end_date").val('');
		}
	});

	var idchallenge_type = $("#id_challenge_type option:selected").val();
	if(idchallenge_type==2){
		$(".field-price").hide('500');
	}
	if(idchallenge_type==1){
		$(".field-price").show('500');
	}
  	
  	$("#id_challenge_type").change(function(){
		var idchallenge_type = $("#id_challenge_type option:selected").val();
		if(idchallenge_type==2){
			$(".field-price").hide('500');
		}
		if(idchallenge_type==1){
			$(".field-price").show('500');
		}
	});
});
