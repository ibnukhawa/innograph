/*
 * jQuery.appear
 * https://github.com/bas2k/jquery.appear/
 * http://code.google.com/p/jquery-appear/
 * http://bas2k.ru/
 *
 * Copyright (c) 2009 Michael Hixson
 * Copyright (c) 2012-2014 Alexander Brovikov
 * Licensed under the MIT license (http://www.opensource.org/licenses/mit-license.php)
 */
(function($) {
    $.fn.appear = function(fn, options) {

        var settings = $.extend({

            //arbitrary data to pass to fn
            data: undefined,

            //call fn only on the first appear?
            one: true,

            // X & Y accuracy
            accX: 0,
            accY: 0

        }, options);

        return this.each(function() {

            var t = $(this);

            //whether the element is currently visible
            t.appeared = false;

            if (!fn) {

                //trigger the custom event
                t.trigger('appear', settings.data);
                return;
            }

            var w = $(window);

            //fires the appear event when appropriate
            var check = function() {

                //is the element hidden?
                if (!t.is(':visible')) {

                    //it became hidden
                    t.appeared = false;
                    return;
                }

                //is the element inside the visible window?
                var a = w.scrollLeft();
                var b = w.scrollTop();
                var o = t.offset();
                var x = o.left;
                var y = o.top;

                var ax = settings.accX;
                var ay = settings.accY;
                var th = t.height();
                var wh = w.height();
                var tw = t.width();
                var ww = w.width();

                if (y + th + ay >= b &&
                    y <= b + wh + ay &&
                    x + tw + ax >= a &&
                    x <= a + ww + ax) {

                    //trigger the custom event
                    if (!t.appeared) t.trigger('appear', settings.data);

                } else {

                    //it scrolled out of view
                    t.appeared = false;
                }
            };

            //create a modified fn with some additional logic
            var modifiedFn = function() {

                //mark the element as visible
                t.appeared = true;

                //is this supposed to happen only once?
                if (settings.one) {

                    //remove the check
                    w.unbind('scroll', check);
                    var i = $.inArray(check, $.fn.appear.checks);
                    if (i >= 0) $.fn.appear.checks.splice(i, 1);
                }

                //trigger the original fn
                fn.apply(this, arguments);
            };

            //bind the modified fn to the element
            if (settings.one) t.one('appear', settings.data, modifiedFn);
            else t.bind('appear', settings.data, modifiedFn);

            //check whenever the window scrolls
            w.scroll(check);

            //check whenever the dom changes
            $.fn.appear.checks.push(check);

            //check now
            (check)();
        });
    };

    //keep a queue of appearance checks
    $.extend($.fn.appear, {

        checks: [],
        timeout: null,

        //process the queue
        checkAll: function() {
            var length = $.fn.appear.checks.length;
            if (length > 0) while (length--) ($.fn.appear.checks[length])();
        },

        //check the queue asynchronously
        run: function() {
            if ($.fn.appear.timeout) clearTimeout($.fn.appear.timeout);
            $.fn.appear.timeout = setTimeout($.fn.appear.checkAll, 20);
        }
    });

    //run checks when these methods are called
    $.each(['append', 'prepend', 'after', 'before', 'attr',
        'removeAttr', 'addClass', 'removeClass', 'toggleClass',
        'remove', 'css', 'show', 'hide'], function(i, n) {
        var old = $.fn[n];
        if (old) {
            $.fn[n] = function() {
                var r = old.apply(this, arguments);
                $.fn.appear.run();
                return r;
            }
        }
    });

})(jQuery);
/* Progress End*/


$(window).scroll(function() {
    if ($(window).scrollTop() >= 250) {
        $('body').addClass('fixed-header');
    } else {
        $('body').removeClass('fixed-header');
    }
});

$(document).ready(function() {


var url_root = $('.url_root').val();


if(!url_root){
    url_root = "http://localhost:8089/"
}

var u = new URL(url_root);

function createBanner3(){

    $.get("/API/load_banner/"+u.host, function(data){
        // alfif
        // $(".result").html( data );
        $.each(data, function( index, value ) {
            if(index == 'banner_satu'){
                var html_img = "";
                $.each(value, function( image, url ) {
                    
                    html_img += "<div class='disable_customize box_slider_satu'>"
                    if(url.url != ''){
                        html_img += "<a href='"+url.url+"' target='blank'>"
                    }
                    html_img += "<img class='disable_customize banner' src='"+url.image+"'/>"
                    if(url.url != ''){
                        html_img += "</a>"
                    }
                    html_img += "</div>"

                    

                });
                $(".header_slider_1").append(html_img);

            }

            if(index == 'banner_dua'){
                var html_img = "";
                $.each(value, function( image, url ) {
                    html_img += "<div class='disable_customize box_slider_sub'>"
                    if(url.url != ''){
                        html_img += "<a href='"+url.url+"' target='blank'>"
                    }
                    html_img += "<img class='disable_customize banner_sub' src='"+url.image+"'/>"
                    if(url.url != ''){
                        html_img += "</a>"
                    }
                    html_img += "</div>"
                });
                $(".header_slider_2").append(html_img);
            }

            if(index == 'banner_tiga'){
                var html_img = "";
                $.each(value, function( image, url ) {

                    html_img += "<div class='disable_customize box_slider_sub'>"
                    if(url.url != ''){
                        html_img += "<a href='"+url.url+"' target='blank'>"
                    }
                    html_img += "<img class='disable_customize banner_sub' src='"+url.image+"'/>"
                    if(url.url != ''){
                        html_img += "</a>"
                    }
                    html_img += "</div>"

                });
                $(".header_slider_3").append(html_img);
            }
        });

        // alert( "Load was performed." );
        $('.header_slider_1').not('.slick-initialized').slick({
            autoplay: true,
            autoplaySpeed: 6000,
            slidesToShow: 1,
            slidesToScroll: 1,
            adaptiveHeight: false,
            dots: false,
            infinite: true,
            arrows: false,
            variableWidth: true,
            responsive: [
                {
                  breakpoint: 1024,
                  settings: {
                    slidesToShow: 1,
                    slidesToScroll: 1
                  }
                },
                {
                  breakpoint: 800,
                  settings: {
                    slidesToShow: 1,
                    slidesToScroll: 1
                  }
                },
                {
                  breakpoint: 480,
                  settings: {
                    slidesToShow: 1,
                    slidesToScroll: 1
                  }
                }
            ]
            

        })
        .on('setPosition', function (event, slick) {
            slick.$slides.css('height', slick.$slideTrack.height() + 'px');
        });

        $('.header_slider_2').not('.slick-initialized').slick({
            autoplay: true,
            autoplaySpeed: 4000,
            slidesToShow: 1,
            adaptiveHeight: false,
            dots: false,
            infinite: true,
            arrows: false,
            variableWidth: true,
            responsive: [
                {
                  breakpoint: 1024,
                  settings: {
                    slidesToShow: 1,
                    slidesToScroll: 1
                  }
                },
                {
                  breakpoint: 800,
                  settings: {
                    slidesToShow: 1,
                    slidesToScroll: 1
                  }
                },
                {
                  breakpoint: 480,
                  settings: {
                    slidesToShow: 1,
                    slidesToScroll: 1
                  }
                }
            ]


        });

        $('.header_slider_3').not('.slick-initialized').slick({
            autoplay: true,
            autoplaySpeed: 3400,
            slidesToShow: 1,
            adaptiveHeight: false,
            dots: false,
            infinite: true,
            arrows: false,
            variableWidth: true,
            responsive: [
                {
                  breakpoint: 1024,
                  settings: {
                    slidesToShow: 1,
                    slidesToScroll: 1
                  }
                },
                {
                  breakpoint: 800,
                  settings: {
                    slidesToShow: 1,
                    slidesToScroll: 1
                  }
                },
                {
                  breakpoint: 480,
                  settings: {
                    slidesToShow: 1,
                    slidesToScroll: 1
                  }
                }
            ]

        });


        // alert($(window).width());
        if($(window).width() < 768){
            $(".header_slider_2").addClass('col-xs-6');
            $(".header_slider_3").addClass('col-xs-6');
        }
        else
        {
            $(".header_slider_2").removeClass('col-xs-6');
            $(".header_slider_3").removeClass('col-xs-6');
        }
        
        
        var width_slider = $(".header_slider_1").width();
        var width_slider_sub = $(".header_slider_2").width();


        $(".box_slider_satu").css("max-width",width_slider);

        $(".banner").css("min-width",width_slider);
        $(".box_slider_sub").css("max-width",width_slider_sub);

        
    });
}


createBanner3();


    $.get("/API/load_category/"+u.host, function(data){
    // alfif
        var html = "";
        $.each(data, function( index, value ) {
            // alert(value.image);
            html += "<div class='disable_customize box_category' style='background-color:"+value.background+"'>"
            html += "<a href='/shop/category/"+value.name_url+"'>"
            html += "<img class='disable_customize' src='"+value.image+"'/>"
            html += "<p class='disable_customize text-center title_product'>"+value.name+"</p>"
            html += "</a>"
            html += "</div>"
        });

        $(".slider_main_category").append(html);


        $('.slider_main_category').not('.slick-initialized').slick({
            // autoplay: true,
            // autoplaySpeed: 4000,
            infinite: true,
            slidesToShow: 6,
            slidesToScroll: 3,
            pagination: true,
            arrows: false,
            responsive: [
                {
                  breakpoint: 1024,
                  settings: {
                    slidesToShow: 5,
                    slidesToScroll: 2,
                  }
                },
                {
                  breakpoint: 800,
                  settings: {
                    slidesToShow: 4,
                    slidesToScroll: 2
                  }
                },
                {
                  breakpoint: 480,
                  settings: {
                    slidesToShow: 3,
                    slidesToScroll: 3
                  }
                }
            ]
        });
        
    });


    function addForYou(){
        var html_li_1 = "" ;
        var html_panel_1 = "" ;
        var html_product_1 = "" ;


        $.get("/API/load_for_you", function(data){
            if(data[0].status == true && data[0].data_products.length > 0){
                
                html_li_1 += "<li role='presentation' id='menu_for_you' class='disable_customize'>";

                html_li_1 += "<a href='#for_you' class='background-blue' aria-controls='more_product' role='tab' data-toggle='tab'>";
                html_li_1 += "<p class='disable_customize text_tabs'>For You</p>";
                html_li_1 += "</a>";
                html_li_1 += "</li>";

                $(".menu_tabs").append(html_li_1);
                html_panel_1 += "<div role='tabpanel' class='disable_customize tab-pane' id='for_you'>";
                
                html_panel_1 += "<div class='disable_customize product_panels_for_you' style='background:#ffffff;'>";
                html_panel_1 += "</div>";
                html_panel_1 += "</div>";

                $(".content_slider_tabs").append(html_panel_1);

                
                $.each(data[0].data_products, function( index_product, product ) {

                    html_product_1 += "<div class='disable_customize card card-tab'>";
                    html_product_1 += "<a href='/shop/product/"+product.url_name+"-"+product.id+"?category="+product.id_category+"'>";
                    html_product_1 += "<div class='disable_customize card-header'>";
                    html_product_1 += "<img class='disable_customize banner_tab_slider' src='"+product.image+"' />";
                    html_product_1 += "</div>";
                    html_product_1 += "<div class='disable_customize card-body'>";
                    html_product_1 += "<p class='disable_customize card-text title_product'>"+product.name+"</p>";
                    html_product_1 += "<p class='disable_customize card-text price'>"+product.price_label+"</p>";
                    html_product_1 += "</div>";
                    html_product_1 += "</a>";
                    html_product_1 += "</div>";
                    
                });
                
                $(".product_panels_for_you").append(html_product_1);
                
                $("#for_you").append("<p class='disable_customize pull-right' style='padding-right:10px;'><a href='/shop/tabs/for_you'>...Lihat Semua</a></p>");
                var btn="<div class='button_prev_next'></div>"
                $("#for_you").append(btn);
                var btnInside=" <a class='slick-prev slick-arrow btn-prev' aria-label='Previous' style='display: block;'><i class='fa fa-chevron-left'></i></a><a class='slick-next slick-arrow btn-next'  aria-label='Next' type='button' style='display: block;'><i class='fa fa-chevron-right'></i></a> </div>"
                $(".button_prev_next").html(btnInside);
                
                $('.btn-next').click(function() {
                    $('.product_panels_for_you').slick('slickNext');
                    console.log("test next");        
                });
                $('.btn-prev').click(function() {
                    $('.product_panels_for_you').slick('slickPrev');
                        console.log("test previous");
                });

                $('.product_panels_for_you').not('.slick-initialized').slick({
                    infinite: true,
                    autoplay: true,
                    autoplaySpeed: 10000,
                    slidesToShow: 6,
                    slidesToScroll: 6,
                    pagination: true,
                    arrows: false,
                    responsive: [
                        {
                          breakpoint: 1024,
                          settings: {
                            slidesToShow: 5,
                            slidesToScroll: 5,
                          }
                        },
                        {
                          breakpoint: 800,
                          settings: {
                            slidesToShow: 4,
                            slidesToScroll: 4
                          }
                        },
                        {
                          breakpoint: 480,
                          settings: {
                            slidesToShow: 3,
                            slidesToScroll: 3
                          }
                        }
                    ]
                });

            }
            else{
                $('#menu_for_you').remove();
            }


            $(".menu_tabs li").first().addClass("active");
            $(".tab-pane").first().addClass("active");

        });
    }

    function addTabs(){
        $.get("/API/load_slider_tab/"+u.host, function(data){
            // alfif
                // console.log("url "+u.host);
                $.each(data, function( index, value ) {
                    
                    var html_li = "";
                    var html_panel="";
                    var html_product="";
                    if(index == 0){
                        html_li += "<li role='presentation'  id='"+value.id_tab+"' class='disable_customize'>";

                        html_li += "<a href='#more_product"+index+"' class='background-blue' aria-controls='more_product' role='tab' data-toggle='tab'>";
                        html_li += "<p class='disable_customize text_tabs'>"+value.name_tab+"</p>";
                    }
                    else
                    {
                        html_li += "<li role='presentation' id='"+value.id_tab+"'>";

                        html_li += "<a href='#more_product"+index+"' class='background-blue' id='text_tabs' aria-controls='more_product' role='tab' data-toggle='tab'>";
                        html_li += "<p class='disable_customize text_tabs'>"+value.name_tab+"</p>";
                    }

                    html_li += "</a>";
                    html_li += "</li>";
                    

                    
                    if(index == 0){
                        html_panel += "<div role='tabpanel' class='disable_customize tab-pane' id='more_product"+index+"'>";
                    }
                    else
                    {
                        html_panel += "<div role='tabpanel' class='disable_customize tab-pane' id='more_product"+index+"'>";
                    }
                    html_panel += "<div class='disable_customize product_panels"+index+"' style='background:#ffffff;'>";
                    html_panel += "</div>";
                    html_panel += "</div>";


                    $(".menu_tabs").append(html_li);
                    $(".content_slider_tabs").append(html_panel);


                    $.each(value.data_products, function( index_product, product ) {

                        html_product += "<div class='disable_customize card card-tab'>";
                        html_product += "<a href='/shop/product/"+product.url_name+"-"+product.id+"?category="+product.id_category+"'>";
                        html_product += "<div class='disable_customize card-header'>";
                        html_product += "<img class='disable_customize banner_tab_slider' src='"+product.image+"' />";
                        html_product += "</div>";
                        html_product += "<div class='disable_customize card-body'>";
                        html_product += "<p class='disable_customize card-text title_product'>"+product.name+"</p>";
                        html_product += "<p class='disable_customize card-text price'>"+product.price_label+"</p>";
                        html_product += "</div>";
                        html_product += "</a>";
                        html_product += "</div>";
                        
                    });

                    $(".product_panels"+index).append(html_product);
                    
                    $("#more_product"+index).append("<p class='disable_customize pull-right' style='padding-right:10px;'><a href='/shop/tabs/"+value.id_tab+"'>...Lihat Semua</a></p>");
                    
                    var btn="<div class='button_prev_next'> <a class='slick-prev slick-arrow btn-prev"+index+"' aria-label='Previous' style='display: block;'><i class='fa fa-chevron-left'></i></a><a class='slick-next slick-arrow btn-next"+index+"'  aria-label='Next' type='button' style='display: block;'><i class='fa fa-chevron-right'></i></a> </div>"

                    $("#more_product"+index).append(btn);


                    $('.btn-next'+index).click(function() {
                        $('.product_panels'+index).slick('slickNext');
                        console.log("test next product_panels"+index);        
                    });
                    
                    $('.btn-prev'+index).click(function() {
                        $('.product_panels'+index).slick('slickPrev');
                        console.log("test previous product_panels"+index);
                    });

                    $('.product_panels'+index).not('.slick-initialized').slick({
                        infinite: true,
                        autoplay: true,
                        autoplaySpeed: 10000,
                        slidesToShow: 6,
                        slidesToScroll: 6,
                        pagination: true,
                        arrows: false,
                        responsive: [
                            {
                            breakpoint: 1024,
                            settings: {
                                slidesToShow: 5,
                                slidesToScroll: 5,
                            }
                            },
                            {
                            breakpoint: 800,
                            settings: {
                                slidesToShow: 4,
                                slidesToScroll: 4
                            }
                            },
                            {
                            breakpoint: 480,
                            settings: {
                                slidesToShow: 3,
                                slidesToScroll: 3
                            }
                            }
                        ]
                    });
                    
                });    
            
                $(".menu_tabs li").first().addClass("active");
                $(".tab-pane").first().addClass("active");    
        });
    }    
    
    function setViewTabs(){
        addForYou();
        addTabs();

    }
    setViewTabs();

    // $("#as-pro-slide").owlCarousel({
    //     items: 4,
    //     margin: 30,
    //     navigation: true,
    //     pagination: false,
    //     responsive: {
    //         0: {
    //             items: 1,
    //         },
    //         481: {
    //             items: 2,
    //         },
    //         768: {
    //             items: 3,
    //         },
    //         1024: {
    //             items: 4,
    //         }
    //     }

    // });

    // $("#as-featured-slide").owlCarousel({
    //     items: 4,
    //     margin: 30,
    //     navigation: true,
    //     pagination: false,
    //     responsive: {
    //         0: {
    //             items: 1,
    //         },
    //         481: {
    //             items: 2,
    //         },
    //         768: {
    //             items: 3,
    //         },
    //         1024: {
    //             items: 4,
    //         }
    //     }

    // });

    // $("#as_our_brand").owlCarousel({
    //     items: 6,
    //     margin: 10,
    //     navigation: true,
    //     pagination: false,
    //     responsive: {
    //         0: {
    //             items: 2,
    //         },
    //         481: {
    //             items: 2,
    //         },
    //         768: {
    //             items: 4,
    //         },
    //         1024: {
    //             items: 8,
    //         }
    //     }

    // });

    // $("#pro_detail_zoom").owlCarousel({
    //     items:4,
    //     margin: 10,
    //     navigation: true,
    //     pagination: false
    // });

    $.get("/API/multiple_category/"+u.host, function(data){
        // alfif
            $.each(data, function( index, value ) {
                var html_box = "";
                var html_card = "";
                html_box += "<div class='disable_customize col-sm-6 col-md-6 col-xs-12'>";
                html_box += "<h5 class='disable_customize'>"+value.title+"</h5>";
                html_box += "<hr class='disable_customize'>";
                html_box += "<div class='disable_customize slider_category_"+index+"'>";
                html_box += "</div>";
                html_box += "</div>";
                // alert(value.title);

                $.each(value.data_product, function( index, product) {
                    html_card += "<div class='disable_customize card card-tab'>";
                    html_card += "<a href='/shop/product/"+product.url_name+"-"+product.id+"?category="+product.id_category+"' title='"+product.name+"'>";
                    html_card += "<div class='disable_customize card-header'>";
                    html_card += "<img class='disable_customize banner_tab_slider' src='"+product.image+"' />";
                    html_card += "</div>";
                    html_card += "<div class='disable_customize card-body'>";
                    html_card += "<p class='disable_customize card-text title_product'>"+product.name+"</p>";
                    html_card += "<p class='disable_customize card-text price'>"+product.price_label+"</p>";
                    html_card += "</div>";
                    html_card += "</a>";
                    html_card += "</div>";
                });

                $(".multiple_category").append(html_box);
                $(".slider_category_"+index).append(html_card);
                
                $(".slider_category_"+index).not('.slick-initialized').slick({
                    autoplay: true,
                    autoplaySpeed: 7000,
                    infinite: true,
                    slidesToShow: 3,
                    slidesToScroll: 3,
                    pagination: true,
                    arrows: false,
                    responsive: [
                        {
                          breakpoint: 1024,
                          settings: {
                            slidesToShow: 3,
                            slidesToScroll: 3,
                          }
                        },
                        {
                          breakpoint: 600,
                          settings: {
                            slidesToShow: 3,
                            slidesToScroll: 3
                          }
                        },
                        {
                          breakpoint: 480,
                          settings: {
                            slidesToShow: 3,
                            slidesToScroll: 3
                          }
                        }
                    ]
                });
            });
            
    });



    /*
    $('.slider_category_2').slick({
        infinite: true,
        slidesToShow: 3,
        slidesToScroll: 3,
        pagination: true,
        arrows: false,
    });

    $('.slider_category_3').slick({
        infinite: true,
        slidesToShow: 3,
        slidesToScroll: 3,
        pagination: true,
        arrows: false,
    });

    $('.slider_category_4').slick({
        infinite: true,
        slidesToShow: 3,
        slidesToScroll: 3,
        pagination: true,
        arrows: false,
    });

    */
    

    /*$(".view-mode .shift_list_view").click(function(e) {
        e.preventDefault();
        $('#products_grid').addClass("list-view-box");
        
    });
    $(".view-mode .shift_grid_view").click(function(e) {
        e.preventDefault();
        $('#products_grid').removeClass("list-view-box");
    });*/

    /* list grid view 
    ===================*/
    $(".oe_website_sale .shift_list_view").click(function(e) {
        $(".oe_website_sale .shift_grid_view").removeClass('active')
        $(this).addClass('active')
        $('#products_grid').addClass("list-view-box");
        localStorage.setItem("product_view", "list");
    });
    $(".oe_website_sale .shift_grid_view").click(function(e) {
        $(".oe_website_sale .shift_list_view").removeClass('active')
        $(this).addClass('active')
        $('#products_grid').removeClass("list-view-box");
        localStorage.setItem("product_view", "grid");
    });
    if (localStorage.getItem("product_view") == 'list') {
        $(".oe_website_sale .shift_grid_view").removeClass('active')
        $(".oe_website_sale .shift_list_view").addClass('active')
        $('#products_grid').addClass("list-view-box");
    }
    if (localStorage.getItem("product_view") == 'grid') {
        $(".oe_website_sale .shift_list_view").removeClass('active')
        $(".oe_website_sale .shift_grid_view").addClass('active')
        $('#products_grid').removeClass("list-view-box");
    }


    /*full width banner*/

      function setWidth(){
        // alfif
        // add function to set width in slick slider
    
        var width_slider = $(".header_slider_1").width();
        var width_slider_sub = $(".header_slider_2").width();

        $(".box_slider_satu").css("max-width",width_slider);

        $(".banner").css("min-width",width_slider);
        $(".box_slider_sub").css("max-width",width_slider_sub);
      }

      function setHeight() {
        windowHeight = $(window).innerHeight() - $('header').outerHeight();
        $('.as-animated-slider .slide').css('min-height', windowHeight);
      };

      setHeight();
      
      $(window).resize(function() {
        
        if($(window).width() < 768){
            $(".header_slider_2").addClass('col-xs-6');
            $(".header_slider_3").addClass('col-xs-6');
        }
        else
        {
            $(".header_slider_2").removeClass('col-xs-6');
            $(".header_slider_3").removeClass('col-xs-6');
        }
        
        setHeight();
        setWidth();
        // alert($(window).width());
        
        // if($(window).width() > 767)
      });

      /**/

      /* Progress
      /-----------------------------------------------*/
	  
       if ($("[data-animate-width]").length>0) {
            $("[data-animate-width]").each(function() {
                $(this).appear(function() {
                    $(this).animate({
                        width: $(this).attr("data-animate-width")
                    }, 800 );
                }, {accX: 0, accY: -100});
            });
        };

        
      

        // Gallery 
        //-----------------------------
        if ($(".slider-popup-img") && $(".slider-popup-img").length > 0) {
           $(".slider-popup-img").magnificPopup({
               type:"image",
               gallery: {
                   enabled: true,
               }
           });
       }
		$('img.theme-slider-gallary').on('load', function (ev) {
			var $link = $(ev.currentTarget);
			var a=$link.parent().find("a");
			a.attr('href',this.src);		
		});
        if ($(".slider-popup-product") && $(".slider-popup-product").length > 0) {
           $(".slider-popup-product").magnificPopup({
               type:"image",
               gallery: {
                   enabled: true,
               }
           });
       }

});


jQuery(document).ready(function($) {
    // browser window scroll (in pixels) after which the "back to top" link is shown
    var offset = 300,
        //browser window scroll (in pixels) after which the "back to top" link opacity is reduced
        offset_opacity = 1200,
        //duration of the top scrolling animation (in ms)
        scroll_top_duration = 700,
        //grab the "back to top" link
        $back_to_top = $('.cd-top');

    //hide or show the "back to top" link
    $(window).scroll(function() {
        ($(this).scrollTop() > offset) ? $back_to_top.addClass('cd-is-visible'): $back_to_top.removeClass('cd-is-visible cd-fade-out');
        if ($(this).scrollTop() > offset_opacity) {
            $back_to_top.addClass('cd-fade-out');
        }
    });

    //smooth scroll to top
    $back_to_top.on('click', function(event) {
        event.preventDefault();
        $('body,html').animate({
            scrollTop: 0,
        }, scroll_top_duration);
    });


    //Mobile menu
   $(".mm-mega-menu > a").click(function(event) {
       event.preventDefault();
       $(this).parent().toggleClass("open-mob-menu");
       $(this).toggleClass("mob-menu-open");
   });

    $(".hm-search .hm-search-hide").click(function() {
        $('body').toggleClass("hm-search-open");
    });
    


    // zoom slider

$('.main_image .img').elevateZoom({
        constrainType:"height", 
        constrainSize:274, 
        zoomType: "lens",
        lensShape: "square",
        containLensZoom: true, 
        gallery:'gallery_01', 
        cursor: 'pointer', 
        galleryActiveClass: "active"
    });
$('.js_variant_img').elevateZoom({
        constrainType:"height", 
        constrainSize:274, 
        zoomType: "lens",
        lensShape: "square",
        containLensZoom: true, 
        gallery:'gallery_01', 
        cursor: 'pointer', 
        galleryActiveClass: "active"
    });

    $('.counter-portfolio').counterUp({
        delay: 20,
        time: 1000
    });
    $('.counter-blog-template').counterUp({
        delay: 20,
        time: 1000
    });
    $('.counter-shortcut').counterUp({
        delay: 20,
        time: 1000
    });
    $('.counter-like').counterUp({
        delay: 20,
        time: 1000
    });



});

 
 

