package idealised.DPIA.FunctionalPrimitives

import idealised.DPIA.Compilation.{TranslationContext, TranslationToImperative}
import idealised.DPIA.DSL._
import idealised.DPIA.Phrases.VisitAndRebuild.Visitor
import idealised.DPIA.Phrases._
import idealised.DPIA.Semantics.OperationalSemantics.{Data, Store}
import idealised.DPIA.Types._
import idealised.DPIA._
import lift.{core => lc}

import scala.language.reflectiveCalls
import scala.xml.Elem

object ForeignFunction {
  val Declaration: lc.ForeignFunction.Decl.type = lc.ForeignFunction.Decl
  val Definition: lc.ForeignFunction.Def.type = lc.ForeignFunction.Def
  type Declaration = lc.ForeignFunction.Decl
  type Definition = lc.ForeignFunction.Def
}

final case class ForeignFunction(funDecl: ForeignFunction.Declaration,
                                 inTs: Seq[DataType],
                                 outT: DataType,
                                 args: Seq[Phrase[ExpType]])
  extends ExpPrimitive {

  override val t: ExpType =
    (inTs zip args).foreach {
      case (inT, arg) => arg :: exp"[$inT, $read]"
    } ->: exp"[$outT, $read]"

  override def eval(s: Store): Data = ???

  override def acceptorTranslation(A: Phrase[AccType])
                                  (implicit context: TranslationContext): Phrase[CommType] = {
    import TranslationToImperative._

    def recurse(ts: Seq[(Phrase[ExpType], DataType)],
                exps: Seq[Phrase[ExpType]],
                inTs: Seq[DataType]): Phrase[CommType] = {
      ts match {
        // with only one argument left to process return the assignment of the function call
        case Seq((arg, inT)) =>
          con(arg)(λ(exp"[$inT, $read]")(e =>
            A :=| outT | ForeignFunction(funDecl, inTs :+ inT, outT, exps :+ e)))
        // with a `tail` of arguments left, recurse
        case Seq((arg, inT), tail@_*) =>
          con(arg)(λ(exp"[$inT, $read]")(e => recurse(tail, exps :+ e, inTs :+ inT)))
      }
    }

    recurse(args zip inTs, Seq(), Seq())
  }

  override def mapAcceptorTranslation(f: Phrase[ExpType ->: ExpType], A: Phrase[AccType])
                                     (implicit context: TranslationContext): Phrase[CommType] =
    ???

  override def continuationTranslation(C: Phrase[ExpType ->: CommType])
                                      (implicit context: TranslationContext): Phrase[CommType] = {
    import TranslationToImperative._

    def recurse(ts: Seq[(Phrase[ExpType], DataType)],
                exps: Seq[Phrase[ExpType]],
                inTs: Seq[DataType]): Phrase[CommType] = {
      ts match {
        // with only one argument left to process return the assignment of the function call
        case Seq( (arg, inT) ) =>
          con(arg)(λ(exp"[$inT, $read]")(e =>
            C( ForeignFunction(funDecl, inTs :+ inT, outT, exps :+ e) )) )
        // with a `tail` of arguments left, recurse
        case Seq( (arg, inT), tail@_* ) =>
          con(arg)(λ(exp"[$inT, $read]")(e => recurse(tail, exps :+ e, inTs :+ inT) ))
      }
    }

    recurse(args zip inTs, Seq(), Seq())
  }

  override def prettyPrint: String = s"${funDecl.name}(${args.map(PrettyPhrasePrinter(_)).mkString(",")})"

  override def xmlPrinter: Elem =
    <ForeignFunction name={ToString(funDecl.name)} inTs={ToString(inTs)} outT={ToString(outT)}>
      {args.map(Phrases.xmlPrinter(_))}
    </ForeignFunction>

  override def visitAndRebuild(f: Visitor): Phrase[ExpType] = {
    ForeignFunction(funDecl, inTs.map(f.data), f.data(outT), args.map(VisitAndRebuild(_, f)))
  }
}
