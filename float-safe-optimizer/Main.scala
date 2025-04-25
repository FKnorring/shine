package float_safe_optimizer

import util.gen
import rise.core.Expr
import rise.core.DSL.ToBeTyped

object Main {
  def main(args: Array[String]): Unit = {
    val name = args(0)
    val exprSourcePath = args(1)
    val outputPath = args(2)
    val useMPFR = args.length > 3 && args(3).toBoolean
    val skipOptimize = args.length > 4 && args(4).toBoolean
    println(s"useMPFR: $useMPFR")
    println(s"skipOptimize: $skipOptimize")

    val exprSource = util.readFile(exprSourcePath)
    val untypedExpr = parseExpr(prefixImports(exprSource))
    val typedExpr = untypedExpr.toExpr
    val finalExpr = Optimize(typedExpr, skipOptimize)
    val code = if (useMPFR) {
      gen.mpfr.function.asStringFromExpr(finalExpr)
    } else {
      gen.openmp.function.asStringFromExpr(finalExpr)
    }
    util.writeToPath(outputPath, code)
  }

  def prefixImports(source: String): String =
    s"""
       |import rise.core.DSL._
       |import rise.core.DSL.Type._
       |import rise.core.DSL.HighLevelConstructs._
       |import rise.core.primitives._
       |import rise.core.types._
       |import rise.core.types.DataType._
       |import rise.openmp.DSL._
       |import rise.openmp.primitives._
       |$source
       |""".stripMargin

  def parseExpr(source: String): ToBeTyped[Expr] = {
    import scala.reflect.runtime.universe
    import scala.tools.reflect.ToolBox

    val toolbox = universe.runtimeMirror(getClass.getClassLoader).mkToolBox()
    toolbox.eval(toolbox.parse(source)).asInstanceOf[ToBeTyped[Expr]]
  }
}
