function LineColors(){

    return d3.scale.ordinal()
      .range(["#0000FF","#FF00FF","#00FF00","#FFFF00","#00FFFF","#845B47","#0080FF","#FF8000","#F4A460","#FFDEAD", "#D2691E","#C71585","#800080","#48D1CC","#006400","#B8860B","#FF4500","#FF6347"]);

  }

function AppendText(vis, texts ){
return vis.append("text")
            .attr("text-anchor", "middle")  // this makes it easy to centre the text as the transform is applied to the anchor
            .attr("transform", "translate("+ (window.GPADDING/2) +","+(window.GHEIGHT/2)+")rotate(-90)")  // text is drawn off the screen top left, move down and out and rotate
            .text(texts);
}