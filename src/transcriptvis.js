$(document).ready(function(){

  // $("span").hover(function(){
  //   // console.log($(this).attr("matched-index"))
  //   $(this).toggleClass("highlight");
  //   $(this).siblings(".aligned").toggleClass("highlight");
  // });
  $('span').hover(function(){
    index_str = $(this).attr("aligned-index")
    tokenScource = $(this).attr('class')
    console.log(tokenScource)
    $(this).addClass("highlight")
    if (tokenScource == "ref") {
      $('span.hyp[index='+index_str+']').addClass("highlight")
    }
  }, function(){
    // tokenScource = $(this).attr('class')
    $(this).removeClass('highlight')
    if (tokenScource == "ref") {
      $('span.hyp[index='+index_str+']').removeClass("highlight")
    }
  })

  // $('span[matched-index]').hover(function(){
  //   $(this).toggleClass("highlight")
  //   index_str = $(this).attr("matched-index")
  //   matched_index_arr = index_str.split('-')
  //   matched_speaker = matched_index_arr[0]
  //   matched_index = matched_index_arr[1]
  //   $('#'+index_str).toggleClass("highlight")
  // })
  $('.metric-container.WDER').click(function() {
    console.log("click")
    var span = $('span[wder_err="error"]');
    if (span.css('color') == 'rgb(128, 0, 0)') {
      span.css('color', '');
    } else {
      span.css('color', 'rgb(128, 0, 0)');
    }
    // $('span[wder_err="error"]').css('color', 'red');
  });


});