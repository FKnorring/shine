package idealised.DPIA.FunctionalPrimitives

import idealised.DPIA.Compilation.RewriteToImperative
import idealised.DPIA.DSL._
import idealised.DPIA.ImperativePrimitives.ScatterAcc
import idealised.DPIA.Phrases.VisitAndRebuild.Visitor
import idealised.DPIA.Phrases._
import idealised.DPIA.Semantics.OperationalSemantics
import idealised.DPIA.Semantics.OperationalSemantics._
import idealised.DPIA.Types._
import idealised.DPIA.{Phrases, _}
import idealised.OpenCL

import scala.xml.Elem

final case class Scatter(n: Nat,
                         dt: DataType,
                         idxF: Phrase[ExpType -> ExpType],
                         array: Phrase[ExpType])
  extends ExpPrimitive
{
  override def `type`: ExpType =
    (n: Nat) -> (dt: DataType) ->
      (idxF :: t"exp[idx($n)] -> exp[idx($n)]") ->
        (array :: exp"[$n.$dt]") ->
          exp"[$n.$dt]"

  override def eval(s: Store): OperationalSemantics.Data = ???

  override def acceptorTranslation(A: Phrase[AccType]): Phrase[CommandType] = {
    import RewriteToImperative._

    acc(array)(ScatterAcc(n, dt, idxF, A))
  }

  override def continuationTranslation(C: Phrase[->[ExpType, CommandType]]): Phrase[CommandType] = {
    import RewriteToImperative._

    `new`(dt"[$n.$dt]", OpenCL.GlobalMemory, λ(exp"[$n.$dt]" x acc"[$n.$dt]")(tmp =>
      acc(this)(tmp.wr) `;` C(tmp.rd) ))
  }


  override def prettyPrint: String = s"(scatter idxF ${PrettyPhrasePrinter(array)})"

  override def xmlPrinter: Elem =
    <scatter>
      <idxF>{Phrases.xmlPrinter(idxF)}</idxF>
      <input>{Phrases.xmlPrinter(array)}</input>
    </scatter>

  override def visitAndRebuild(f: VisitAndRebuild.Visitor): Phrase[ExpType] =
    Scatter(f(n), f(dt), VisitAndRebuild(idxF, f), VisitAndRebuild(array, f))
}
