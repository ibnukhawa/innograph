odoo.define('theme_stoneware.collapsed_menu',function(require){
	function autocollapse() {
	    var navbars = $('.sidemenu-auto-collapsed');
	    console.log('calledd!!')
	    $.each(navbars, function(k,navbar){
	    	console.log('calledd!!',navbar)
	    	var thiselm = $(navbar)
	    	// thiselm.removeClass('collapse')
	    	console.log($(window).innerWidth())
		    if($(window).innerWidth() < 770){
		    	console.log('will hide')
		        // thiselm.addClass('collapse')
		        $(thiselm).collapse('hide')
		    }else{
		    	console.log('will show')
		    	// thiselm.removeClass('collapse')
		    	$(thiselm).collapse('show')
		    }
	    })

	}

	function assign_collapse_button(){
		// $.each($('.btn-toggle-autocollapse-menu'), function(k,btn){
			var btn = $('.btn-toggle-autocollapse-menu')
			var sidemenu = $('.sidemenu-auto-collapsed')
			$(btn).on('click', function(){
				console.log('clicked',sidemenu.attr('class'))
				// $(sidemenu).toggleClass('collapse')
				$(sidemenu).collapse('toggle')
			})
		// })
	}

	$(document).ready(function(){
		autocollapse()
		assign_collapse_button()
	})
	$(window).on('resize', function(){
		autocollapse()
	})
	
})