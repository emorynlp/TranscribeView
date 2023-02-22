

$(document).ready(function(){

  // array of colors for different speakers
  let colors = ["ef476f", "118ab2", "06d6a0", "83d483", "f78c6b", "0cb0a9","ffd166", "073b4c"]

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


  // console.log($(".speaker-mapping").text())
  // Ref to Hyp SpeakerMapping
  var speakerMap = JSON.parse($(".speaker-mapping").text());


  // Loop over the IDs in the mapping object
  let i = 0;
  for (let id in speakerMap) {
    // Get the corresponding spans using the ID selector
    console.log(id)
    let $sourceSpans = $("[id='" + id + "']");
    let $refUtteranceDivs = $("div.inner-utterance[speakerid='" + id + "']");
    let $targetSpans = $("[id='" + speakerMap[id] + "']");
    let $hypUtteranceDivs = $("div.inner-utterance[speakerid='" + speakerMap[id] + "']");
    
    // Add a class to set the color based on the index
    $sourceSpans.addClass("mapped-speakers " + "pair" + i);
    $sourceSpans.css("color", colors[i])
    $refUtteranceDivs.css( "border-left", "2px solid #" + colors[i])

    $targetSpans.addClass("mapped-speakers " + "pair"+ i);
    $targetSpans.css("color", colors[i])
    $hypUtteranceDivs.css( "border-left", "2px solid #" + colors[i])
    console.log("2px solid " + colors[i])
    i++;
  }

  // Add an "unmatched" class to the remaining spans
  $('span.speaker').not("[class*='mapped-speakers']").addClass("unmatched-speakers");
});